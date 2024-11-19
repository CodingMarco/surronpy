import asyncio
from machine import UART

uart0 = UART(0, tx=3, rx=4)
uart1 = UART(1, tx=5, rx=6)
uart0.init(baudrate=9600, bits=8, parity=None, stop=1)
uart1.init(baudrate=9600, bits=8, parity=None, stop=1)


async def sender():
    swriter = asyncio.StreamWriter(uart0, {})
    while True:
        swriter.write("    " * 10)
        await swriter.drain()
        await asyncio.sleep(0.1)


async def receiver():
    swriter = asyncio.StreamWriter(uart1, {})
    while True:
        swriter.write("ZZZZ" * 10)
        await swriter.drain()
        await asyncio.sleep(0.1)


async def main():
    asyncio.create_task(sender())
    asyncio.create_task(receiver())
    while True:
        await asyncio.sleep(1)


def test():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        asyncio.new_event_loop()
        print("as_demos.auart.test() to run again.")


test()
