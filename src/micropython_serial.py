import asyncio
import machine

SURRON_BAUDRATE = 9600


class MicropythonSerial:
    def __init__(self, tx_pin: int, rx_pin: int, tx_enable_pin: int):
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self._create_and_init_uart()
        self.tx_enable_pin = tx_enable_pin
        self.tx_enable = machine.Pin(tx_enable_pin, machine.Pin.OUT)
        self.sreader = asyncio.StreamReader(self.uart, {})
        self.swriter = asyncio.StreamWriter(self.uart, {})

    async def readinto(self, buf: memoryview, length: int, timeout_ms: int):
        self.tx_enable.value(0)
        future = self.sreader.readinto(buf[:length])
        try:
            await asyncio.wait_for_ms(future, timeout_ms)
        except asyncio.TimeoutError:
            return 0

    async def write(self, data: bytes):
        self.tx_enable.value(1)
        self.swriter.write(data)
        await self.swriter.drain()

        # drain() doesn't work here so we wait for the UART to finish sending
        while not self.uart.txdone():
            await asyncio.sleep_ms(1)

        self.tx_enable.value(0)

    def reset_input_buffer(self):
        pass

    def close(self):
        self.uart.deinit()

    def reset(self):
        self.close()
        self._create_and_init_uart()
        self.tx_enable.value(0)

    def _create_and_init_uart(self):
        self.uart = machine.UART(0, tx=self.tx_pin, rx=self.rx_pin)
        # We run with no UART timeout: UART read never blocks.
        self.uart.init(SURRON_BAUDRATE, tx=self.tx_pin, rx=self.rx_pin, timeout=0)
