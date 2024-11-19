from machine import UART

uart0 = UART(0, tx=3, rx=2)
uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=1000)


def test():
    while True:
        uart0.write("adfasdfasdf")


def read_test():
    while True:
        print(uart0.read())


read_test()
