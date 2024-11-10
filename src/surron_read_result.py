from enum import Enum


class SurronReadResult(Enum):
    Success = 1
    Timeout = 2
    InvalidData = 3
