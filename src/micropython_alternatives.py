class date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


class datetime:
    def __init__(self, year, month, day, hour, minute, second):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def isoformat(self):
        return f"{self.year}-{self.month}-{self.day}T{self.hour}:{self.minute}:{self.second}"
