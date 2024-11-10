from enum import Enum


class SurronCmd(Enum):
    ReadRequest = 0x46
    ReadResponse = 0x47
    Status = 0x57
