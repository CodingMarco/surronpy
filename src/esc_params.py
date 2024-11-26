ESC_ADDRESS = 0x183


class EscParameterId:
    def __init__(self, name, value, length):
        self.name = name
        self.value = value
        self.length = length


Unknown_72 = EscParameterId("Unknown_72", 72, 12)
Unknown_75 = EscParameterId("Unknown_75", 75, 2)
