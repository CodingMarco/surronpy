import bms_params
from bms_params import BmsParameterId
from surron_communication import SurronCommunication


class SurronBmsCommunication:
    def __init__(self, comm: SurronCommunication):
        self.comm = comm

    async def read_raw_parameter_data(self, parameter: BmsParameterId) -> bytes | None:
        return await self.comm.read_register(
            bms_params.BMS_ADDRESS,
            parameter.value,
            parameter.length,
        )

    async def read_parameter(self, parameter: BmsParameterId):
        data = await self.read_raw_parameter_data(parameter)
        return bms_params.decode_bms_data(parameter, data)
