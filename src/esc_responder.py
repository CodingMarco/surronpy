import time
import global_data

from surron_communication import SurronCommunication, SurronReadResult
from surron_data_packet import SurronDataPacket, SurronCmd
from transparency import logging
from bms_params import BMS_ADDRESS
from esc_params import ESC_ADDRESS


class EscResponder:
    ESC_RESPONSE_TIMEOUT_SECS = 30

    def __init__(self, esc_comm: SurronCommunication):
        self.esc_comm = esc_comm
        self.last_update = 0
        self.esc_status = global_data.esc_params

    async def run(self):
        while True:
            result: SurronReadResult
            packet: SurronDataPacket | None
            result, packet = await self.esc_comm.receive_packet(1000 * 1000)
            if result == SurronReadResult.Success and packet is not None:
                await self.handle_esc_packet(packet)
            else:
                logging.info(f"Failed to read packet from ESC: {result}")

    async def handle_esc_packet(self, packet: SurronDataPacket):
        if packet.command == SurronCmd.ReadRequest and packet.address == BMS_ADDRESS:
            await self.reply_cached_bms_param_to_esc(packet)
        elif packet.command == SurronCmd.Status and packet.address == ESC_ADDRESS:
            # We don't do anything with this (unknown) data yet and just keep the raw data as good practice.
            self.esc_status[packet.parameter] = packet.command_data
            global_data.esc_params_updated = True
        else:
            logging.info(f"Unknown packet from ESC: {packet}")

    async def reply_cached_bms_param_to_esc(self, request_packet: SurronDataPacket):
        response_data = self.get_cached_value(request_packet.parameter)
        if (
            response_data is None
            or time.time() - self.last_update > self.ESC_RESPONSE_TIMEOUT_SECS
        ):
            logging.info(f"Parameter {request_packet.parameter} missing or outdated")
            return

        response_packet = SurronDataPacket.create(
            command=SurronCmd.ReadResponse,
            address=request_packet.address,
            parameter=request_packet.parameter,
            data_length=request_packet.data_length,
            data=response_data,
        )

        await self.esc_comm.send_packet(response_packet)

    def get_cached_value(self, param_id: int) -> bytes | None:
        # Current values to respond to read requests.
        # These values are requested periodically from the BMS by us.
        # Dictionary of parameter ID to response bytes.
        data = global_data.bms_params_fast.get(param_id, None)
        if data is None:
            data = global_data.bms_params_slow.get(param_id, None)

        return data
