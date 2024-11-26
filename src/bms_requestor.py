import time
import asyncio
from surron_bms_communication import SurronBmsCommunication


class BmsRequestor:
    FAST_INTERVAL_MS = 1000
    SLOW_DIVIDER = 5

    def __init__(
        self,
        bms_comm: SurronBmsCommunication,
        params_slow: list[int],
        params_fast: list[int],
    ):
        self.bms_comm = bms_comm
        self.params_slow = params_slow
        self.params_fast = params_fast

        self.current_values_slow = dict()
        self.current_values_fast = dict()

    async def run(self):
        update_count = 0
        ticks = time.ticks_ms()
        while True:
            await self.request_params(is_fast=True)
            update_count += 1
            if update_count % self.SLOW_DIVIDER == 0:
                await self.request_params(is_fast=False)

            time_elapsed = time.ticks_diff(time.ticks_ms(), ticks)
            if time_elapsed < self.FAST_INTERVAL_MS:
                await asyncio.sleep_ms(self.FAST_INTERVAL_MS - time_elapsed)

    async def request_params(self, is_fast: bool):
        params = self.params_fast if is_fast else self.params_slow
        current_values = (
            self.current_values_fast if is_fast else self.current_values_slow
        )
        for param in params:
            data = await self.bms_comm.read_raw_parameter_data(param)
            current_values[param] = data
