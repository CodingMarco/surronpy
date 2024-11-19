from struct import pack, unpack


class SurronCmd:
    ReadRequest = 0x46
    ReadResponse = 0x47
    Status = 0x57


class SurronHeader:
    def __init__(self, command: int, address: int, parameter: int, data_length: int):
        self.command = command
        self.address = address
        self.parameter = parameter
        self.data_length = data_length


class SurronDataPacket:
    HEADER_LENGTH = 5

    def __init__(
        self,
        command: int,
        address: int,
        parameter: int,
        data_length: int,
        command_data: bytes | None,
    ):
        self.command = command
        self.address = address
        self.parameter = parameter
        self.data_length = data_length
        self.command_data = command_data

    @staticmethod
    def create(
        command: int,
        address: int,
        parameter: int,
        data_length: int,
        command_data: bytes | None,
    ):
        if (
            command == SurronCmd.ReadRequest
            and command_data is not None
            and len(command_data) > 0
        ):
            raise ValueError("ReadRequest command may not have command data")
        if command in (SurronCmd.ReadResponse, SurronCmd.Status) and (
            command_data is None or len(command_data) != data_length
        ):
            raise ValueError(
                "ReadResponse/Status command must have command data with length equal to data_length"
            )

        return SurronDataPacket(command, address, parameter, data_length, command_data)

    @staticmethod
    def from_bytes(data: bytes):
        if len(data) < 6:
            raise ValueError("Message too short (less than 6 bytes)")

        calc_checksum = SurronDataPacket.calc_checksum(data[:-1])
        read_checksum = data[-1]

        if read_checksum != calc_checksum:
            SurronDataPacket.handle_data_error(
                f"Invalid checksum (calculated: {calc_checksum:02X}, read: {read_checksum:02X})"
            )
            return None

        header = SurronDataPacket.read_header(data[: SurronDataPacket.HEADER_LENGTH])
        if header is None:
            return None

        expected_length = SurronDataPacket.get_packet_length(
            header.command, header.data_length
        )
        if len(data) != expected_length:
            SurronDataPacket.handle_data_error(
                f"Message too short (expected {expected_length}, got {len(data)})"
            )
            return None

        command_data = (
            None
            if header.command == SurronCmd.ReadRequest
            else data[5 : 5 + header.data_length]
        )

        return SurronDataPacket.create(
            header.command,
            header.address,
            header.parameter,
            header.data_length,
            bytes(command_data),
        )

    def to_bytes(self) -> bytes:
        length = SurronDataPacket.get_packet_length(self.command, self.data_length)
        bytes_data = bytearray(length)
        bytes_data[0] = self.command
        bytes_data[1:3] = pack("<H", self.address)
        bytes_data[3] = self.parameter
        bytes_data[4] = (
            self.data_length + 1
            if self.command == SurronCmd.Status
            else self.data_length
        )

        if self.command != SurronCmd.ReadRequest and self.command_data:
            bytes_data[5 : 5 + self.data_length] = self.command_data

        bytes_data[-1] = SurronDataPacket.calc_checksum(bytes_data[:-1])
        return bytes(bytes_data)

    @staticmethod
    def calc_checksum(data: bytes) -> int:
        return sum(data) % 256

    @staticmethod
    def read_header(header: bytes) -> SurronHeader | None:
        if len(header) < SurronDataPacket.HEADER_LENGTH:
            raise ValueError(
                f"Header must be at least {SurronDataPacket.HEADER_LENGTH} bytes long"
            )

        command = header[0]
        if command not in (
            SurronCmd.Status,
            SurronCmd.ReadResponse,
            SurronCmd.ReadRequest,
        ):
            SurronDataPacket.handle_data_error(f"Command 0x{command:X} is not valid.")
            return None

        address = unpack("<H", header[1:3])[0]
        parameter = header[3]
        data_length = header[4] - 1 if command == SurronCmd.Status else header[4]
        return SurronHeader(command, address, parameter, data_length)

    @staticmethod
    def handle_data_error(error: str):
        raise ValueError(f"Data error: {error}")

    @staticmethod
    def get_packet_length_from_header(header_bytes: bytes) -> int:
        header = SurronDataPacket.read_header(header_bytes)
        if header is None:
            return -1
        return SurronDataPacket.get_packet_length(header.command, header.data_length)

    @staticmethod
    def get_packet_length(command: SurronCmd, data_length: int) -> int:
        return (
            1  # command
            + 2  # address
            + 1  # parameter
            + 1  # parameterlength
            + (0 if command == SurronCmd.ReadRequest else data_length)  # data
            + 1  # checksum
        )

    def __str__(self) -> str:
        command_str = {
            SurronCmd.ReadRequest: "ReadRequest",
            SurronCmd.ReadResponse: "ReadResponse",
            SurronCmd.Status: "Status",
        }.get(self.command, "[Invalid]")

        command_data_str = self.command_data.hex() if self.command_data else ""
        return f"{command_str} {self.address:04X} {self.parameter:02X} - {command_data_str}"
