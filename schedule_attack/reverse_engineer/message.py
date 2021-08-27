from ..base.message import Message

class REVMessage(Message):

    def __init__(self, id, dlc, data, timestamp, transmission_time):
        super(REVMessage, self).__init__(id, dlc, data, transmission_time)
        self.timestamp = timestamp


    def __str__(self):
        return "id : {}, dlc: {}, data: {}, offset: {}, Transmission: {}".format(self.id,self.dlc, self.data, self.offset, self.transmission_time, self.timestamp)
