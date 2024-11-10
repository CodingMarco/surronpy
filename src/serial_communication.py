import serial

SURRON_BAUDRATE = 9600


class SerialCommunication:
    def __init__(self, port: str):
        self.port = port
        self.serial = serial.Serial(port, SURRON_BAUDRATE, timeout=1)

    def read(self, length: int, timeout: float) -> bytes:
        self.serial.timeout = timeout
        return self.serial.read(length)

    def write(self, data: bytes):
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
