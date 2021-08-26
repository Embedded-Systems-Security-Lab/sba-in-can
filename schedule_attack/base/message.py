from abc import ABC, abstractmethod

class Message(ABC):

    def __init__(self, id, dlc, data, offset, transmission_time):
        super(Message, self).__init__()
        self.id = id
        self.dlc = dlc
        self.data = data
        self.offset = offset
        self.transmission_time = transmission_time


    def __repr__(self):
        return "Message('{}', '{}', '{}', '{}', '{}' )".format(self.id,self.dlc, self.data, self.offset, self.transmission_time)

    def __str__(self):
        return "id : {}, dlc: {}, data: {}, offset: {}, Transmission: {}".format(self.id,self.dlc, self.data, self.offset, self.transmission_time)
