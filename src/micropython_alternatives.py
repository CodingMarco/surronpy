import machine

rtc = machine.RTC()


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

    @staticmethod
    def now():
        # We don't need weekday and subseconds
        year, month, day, _, hours, minutes, seconds, _ = rtc.datetime()
        return datetime(year, month, day, hours, minutes, seconds)


log_level = "DEBUG"


class logging:
    DEBUG = "DEBUG"
    INFO = "INFO"

    @staticmethod
    def basicConfig(level):
        global log_level
        log_level = level

    @staticmethod
    def debug(msg):
        if log_level == "DEBUG":
            print(f"DEBUG: {msg}")

    @staticmethod
    def info(msg):
        print(f"INFO: {msg}")

    @staticmethod
    def log(level, msg):
        print(f"{level}: {msg}")
