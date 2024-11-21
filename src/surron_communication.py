from surron_data_packet import SurronDataPacket, SurronCmd
import time
from transparency import logging


class SurronReadResult:
    Success = 1
    Timeout = 2
    InvalidData = 3


class SurronCommunication:
    def __init__(self, serial):
        self.serial = serial

    async def read_register(
        self, address: int, parameter: int, parameter_length: int
    ) -> bytes | None:
        send_packet = SurronDataPacket.create(
            SurronCmd.ReadRequest, address, parameter, parameter_length, None
        )

        for trial in range(3):
            self.serial.reset_input_buffer()
            await self.serial.write(send_packet.to_bytes())

            # 9600 baud 8N1 = ~960 bytes/s, so 200ms are enough for ~192 bytes.
            # also, BMS takes some time to responsd sometimes when it is busy updating the display (>80ms in some cases)
            result, packet = await self.receive_packet(200)

            if result == SurronReadResult.Success:
                if (
                    packet.address == address
                    and packet.parameter == parameter
                    and packet.data_length == parameter_length
                ):
                    return packet.command_data
                logging.debug(f"Wrong packet received: {packet}")
            elif result == SurronReadResult.Timeout:
                logging.log(
                    logging.DEBUG if trial < 2 else logging.INFO,
                    f"Timeout on trial {trial}",
                )
            elif result == SurronReadResult.InvalidData:
                logging.info("Invalid data")
            else:
                break

            # can not be too high or else BMS goes back into standby (after ~3s)
            time.sleep(0.1)

        return None

    async def receive_packet(
        self, timeout_ms: int
    ) -> tuple[SurronReadResult, SurronDataPacket | None]:
        buffer = bytearray(512)
        buffer_mv = memoryview(buffer)
        buffer_pos = 0
        header_length = SurronDataPacket.HEADER_LENGTH

        await self.serial.readinto(buffer_mv, header_length, timeout_ms)
        if not buffer[0]:
            self.serial.reset()
            return SurronReadResult.Timeout, None
        buffer_pos += header_length

        rest_length = (
            SurronDataPacket.get_packet_length_from_header(buffer[:header_length])
            - header_length
        )
        if rest_length < 0:
            print(f"Invalid data: {buffer[:header_length].hex()}")
            self.serial.reset()
            return SurronReadResult.InvalidData, None

        num_read = await self.serial.readinto(
            buffer_mv[buffer_pos:], rest_length, timeout_ms
        )
        if num_read < rest_length:
            self.serial.reset()
            return SurronReadResult.Timeout, None

        buffer_pos += rest_length

        packet = SurronDataPacket.from_bytes(buffer[:buffer_pos])
        if packet is None:
            self.serial.reset()
            return SurronReadResult.InvalidData, None

        return SurronReadResult.Success, packet
