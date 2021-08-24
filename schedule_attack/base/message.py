from abc import ABC, abstractmethod

class Message(ABC):

    def __init__(self, id, dlc, data, timestamp, transmission_time):
        super(Message, self).__init__()
        self.id = id
        self.dlc = dlc
        self.data = data
        self.timestamp = timestamp
        self.transmission_time = transmission_time

    def __repr__(self):
        return "Message('{}', '{}', '{}', '{}', '{}' )".format(self.id,self.dlc, self.data, self.timestamp, self.transmission_time)

    def __str__(self):
        return "id : {}, dlc: {}, data: {}, timestamp: {}, Transmission: {}".format(self.id,self.dlc, self.data, self.timestamp, self.transmission_time)
