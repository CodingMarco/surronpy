import serial

SURRON_BAUDRATE = 9600


class SerialCommunication:
    def __init__(self, port: str):
        self.port = port
        self.serial = serial.Serial(port, SURRON_BAUDRATE, timeout=1)

    async def readinto(self, buf: memoryview, length: int, timeout_ms: int):
        self.serial.timeout = timeout_ms / 1000
        # data_read = self.serial.read(length)
        # buf[: len(data_read)] = data_read
        # return len(data_read)
        return self.serial.readinto(buf[:length])

    async def write(self, data: bytes):
        self.serial.write(data)
        self.serial.flush()

    def reset_input_buffer(self):
        self.serial.reset_input_buffer()

    def close(self):
        self.serial.close()

    def reset(self):
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.close()
        self.serial.open()
