

class Message(object):

    def __init__(self, id, dlc, data, transmission_time):
        super(Message, self).__init__()
        self.id = id
        self.dlc = dlc
        self.data = data
        self.transmission_time = transmission_time


    def __str__(self):
        return "id : {}, dlc: {}, data: {}, Transmission: {}".format(self.id,self.dlc, self.data, self.transmission_time)
