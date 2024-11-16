from machine import UART

uart0 = UART(0, tx=3, rx=4)
uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=1000, invert=UART.INV_RX)


def test():
    while True:
        uart0.write("adfasdfasdf")


def read_test():
    while True:
        print(uart0.read())


test()
