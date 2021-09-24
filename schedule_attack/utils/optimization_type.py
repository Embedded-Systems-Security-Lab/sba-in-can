from enum import Enum


class Optimization(Enum):

    NO_OPT = 1
    AVERAGE_START_TIME = 2
    INTERSECTION = 3
    AVERAGE_MID_TRANS = 4

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Optimization[s]
        except Exception as e:
            raise ValueError
