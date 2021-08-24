import random
from utils.general import *
from ..base.message import Message

class SIMMessage(Message):

    def __init__(self, id, dlc, period, timestamp, transmission_time,data,release_time, jitter=0):
        super(SIMMessage, self).__init__(id, dlc, data, timestamp, transmission_time)
        self.release_time = release_time
        self.jitter = jitter
        self.is_offset = False
        self.is_jitter = False
        self.is_pending = True
        self.is_active = False
        self.end_transmission = self.transmission_time + self.release_time

    def __lt__(self, other):
        if self.is_active:
            if self.is_active and self.id != other.id:
                return self.id < other.id
            elif self.is_active and (self.release_time + self.jitter) != (other.release_time + other.jitter):
                return self.release_time < other.release_time
        elif self.is_pending:
            return (self.release_time + self.jitter)  < (other.release_time + other.jitter)

    def __iter__(self):
        return iter([self.id, self.dlc, " ".join(self.data), \
            round(self.end_transmission_time, 4), self.release_time, self.period, self.jitter])

    def __str__(self):
        return ("job\ttaskID: " + str(self.id) +
                "\tinstance_no: " + str(self.instance_no) +
                "\tdlc: " + str(self.dlc) +
                "\tTx: " + str(self.transmission_time) +
                "\trelease_time: " + str(self.release_time) +
                "   s_transmission: " + str(self.end_transmission_time - self.transmission_time) +
                "   e_transmission: " + str(self.end_transmission_time))

