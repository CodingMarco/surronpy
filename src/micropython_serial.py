import asyncio
import machine
from time import ticks_add, ticks_diff, ticks_ms


async def _g():
    pass


type_coro = type(_g())


# If a callback is passed, run it and return.
# If a coro is passed initiate it and return.
# coros are passed by name i.e. not using function call syntax.
def launch(func, tup_args):
    res = func(*tup_args)
    if isinstance(res, type_coro):
        res = asyncio.create_task(res)
    return res


class Delay_ms:
    class DummyTimer:  # Stand-in for the timer class. Can be cancelled.
        def cancel(self):
            pass

    _fake = DummyTimer()

    def __init__(self, func=None, args=(), duration=1000):
        self._func = func
        self._args = args
        self._durn = duration  # Default duration
        self._retn = None  # Return value of launched callable
        self._tend = None  # Stop time (absolute ms).
        self._busy = False
        self._trig = asyncio.ThreadSafeFlag()
        self._tout = asyncio.Event()  # Timeout event
        self.wait = self._tout.wait  # Allow: await wait_ms.wait()
        self.clear = self._tout.clear
        self.set = self._tout.set
        self._ttask = self._fake  # Timer task
        self._mtask = asyncio.create_task(self._run())  # Main task

    async def _run(self):
        while True:
            await self._trig.wait()  # Await a trigger
            self._ttask.cancel()  # Cancel and replace
            await asyncio.sleep_ms(0)
            dt = max(ticks_diff(self._tend, ticks_ms()), 0)  # Beware already elapsed.
            self._ttask = asyncio.create_task(self._timer(dt))

    async def _timer(self, dt):
        await asyncio.sleep_ms(dt)
        self._tout.set()  # Only gets here if not cancelled.
        self._busy = False
        if self._func is not None:
            self._retn = launch(self._func, self._args)

    # API
    # trigger may be called from hard ISR.
    def trigger(self, duration=0):  # Update absolute end time, 0-> ctor default
        if self._mtask is None:
            raise RuntimeError("Delay_ms.deinit() has run.")
        self._tend = ticks_add(ticks_ms(), duration if duration > 0 else self._durn)
        self._retn = None  # Default in case cancelled.
        self._busy = True
        self._trig.set()

    def stop(self):
        self._ttask.cancel()
        self._ttask = self._fake
        self._busy = False
        self._tout.clear()

    def __call__(self):  # Current running status
        return self._busy

    running = __call__

    def rvalue(self):
        return self._retn

    def callback(self, func=None, args=()):
        self._func = func
        self._args = args

    def deinit(self):
        if (
            self._mtask is not None
        ):  # https://github.com/peterhinch/micropython-async/issues/98
            self.stop()
            self._mtask.cancel()
            self._mtask = None


class StreamReaderTo(asyncio.StreamReader):
    def __init__(self, source):
        super().__init__(source)
        self._delay_ms = Delay_ms()  # Allocate once only

    # Task cancels itself if timeout elapses without a byte being received
    async def readintotim(
        self, buf: bytearray, toms: int
    ) -> int:  # toms: timeout in ms
        mvb = memoryview(buf)
        timer = self._delay_ms
        timer.callback(asyncio.current_task().cancel)
        timer.trigger(toms)  # Start cancellation timer
        n = 0
        nbytes = len(buf)
        try:
            while n < nbytes:
                n += await super().readinto(mvb[n:])
                timer.trigger(toms)  # Retrigger when bytes received
        except asyncio.CancelledError:
            pass
        timer.stop()
        return n


SURRON_BAUDRATE = 9600


class MicropythonSerial:
    def __init__(self, tx_pin: int, rx_pin: int, tx_enable_pin: int):
        self.uart = machine.UART(0, tx=tx_pin, rx=rx_pin)
        # We run with no UART timeout: UART read never blocks.
        self.uart.init(SURRON_BAUDRATE, tx=tx_pin, rx=rx_pin, timeout=0)
        self.tx_enable_pin = tx_enable_pin
        self.tx_enable = machine.Pin(tx_enable_pin, machine.Pin.OUT)
        self.sreader = StreamReaderTo(self.uart)
        self.swriter = asyncio.StreamWriter(self.uart, {})

    async def readinto(self, buf: memoryview, length: int, timeout_ms: int):
        self.tx_enable.value(0)
        return await self.sreader.readintotim(buf[:length], timeout_ms)

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
        self.uart.deinit()
        self.uart.init(SURRON_BAUDRATE, tx=self.uart.tx, rx=self.uart.rx)
        self.tx_enable.value(0)
