import os
import csv
import math
import sys
from ..utils.general import *
from ..utils.logger import CustomLogger
from .message import REVMessage



class ReverseLogs(object):

    def __init__(self, csv_file, bus_speed, log_file="reverselogger.log"):
        super(ReverseLogs, self).__init__()
        self.bus_speed = bus_speed
        self.log_from_csv(csv_file)
        self.logger = CustomLogger(__name__,log_file)


    def log_from_csv(self, csv_file):
        self.log_list = []
        with open(csv_file, 'r') as file:
          has_header = csv.Sniffer().has_header(file.read(General.HEADER_DATA_BYTE))
          file.seek(0)
          reader = csv.reader(file)
          if has_header:
              next(reader)
          for row in reader:
              ID = int(row[0],16)
              DLC = int(row[1])
              DATA = row[2]
              timestamp = float(row[3])
              transmission_time = General.get_transmission_time(DLC,self.bus_speed)
              self.log_list.append(REVMessage(ID, DLC, DATA, timestamp, transmission_time))

    def find_previous_lower_id(self, index):
        lower_id = index - 1
        while lower_id >= 0:
            if abs(int(self.log_list[lower_id].id)) == abs(int(self.log_list[index].id)):
                return -1
            if float(self.log_list[lower_id+1].timestamp) - float(self.log_list[lower_id].timestamp) \
                        > float(self.log_list[lower_id+1].transmission_time) + General.EPSILON:
                return lower_id + 1

            if abs(int(self.log_list[lower_id].id)) < abs(int(self.log_list[index].id)):
                lower_id -= 1
            else:
                break

        return lower_id

    def period_bounds(self):

        unique_ids = list(set({log.id for log in self.log_list}))
        unique_ids.sort()
        timestamp = 0
        dlc = 0
        phase = 0

        id_list = {}
        unique_id_vars = {}

        """Iterate through the unique ids to find the lower and upper bound"""
        for unique_id in unique_ids:
            instance_of_unique_id = 1
            upper_bound = 10000
            lower_bound = -1
            delta = 1/self.bus_speed
            got_offset = False
            offset_val = None


            for i in range(len(self.log_list)):
                lower = -1
                upper = 1000
                if unique_id == self.log_list[i].id :
                    if instance_of_unique_id > 1:
                        lower_id = i - 1
                        while lower_id >= 0:

                            if abs(int(self.log_list[lower_id].id)) < abs(int(self.log_list[i].id)):
                                lower_id -= 1
                            else:
                                break

                        if (lower_id <= 0):
                            continue
                        if not got_offset and ((self.log_list[i].timestamp - self.log_list[i].transmission_time) > (self.log_list[i-1].timestamp + 0/self.bus_speed)):#+ 3/General.BUS_SPEED
                            offset_val = (self.log_list[i].timestamp - self.log_list[i].transmission_time, instance_of_unique_id-1)
                            got_offset = True

                        timestamp_offset = float(self.log_list[lower_id].timestamp) - timestamp
                        timestamp_offset_1 = float(self.log_list[i].timestamp) - timestamp
                        lower = abs(timestamp_offset - self.log_list[lower_id].transmission_time)/(instance_of_unique_id - 1)
                        upper = abs(timestamp_offset_1 - (self.log_list[i].transmission_time))/(instance_of_unique_id - 1)
                    else:
                        timestamp = self.log_list[i].timestamp - self.log_list[i].transmission_time
                        dlc = self.log_list[i].dlc
                        data = self.log_list[i].data
                    if (abs(upper - lower ) < delta):
                        lower_bound = lower
                        upper_bound = upper
                        instance_of_unique_id += 1
                        delta = abs(upper - lower )
                        break

                    instance_of_unique_id += 1
                    if (round((lower + General.EPSILON),5) < round(lower_bound,5)) or (round(upper,5) > round((upper_bound + General.EPSILON),5)):
                        continue
                    else:
                        if instance_of_unique_id - 1 > 2:
                            if lower > lower_bound:
                                lower_bound = lower
                            if upper < upper_bound:
                                upper_bound = upper

            tightBound = round(1 - ((float(round(upper_bound, 6)) - float(round(lower_bound, 6)))/float(upper_bound)), 6)


            output = []
            jitter = 0
            if offset_val != None:
                timestamp = offset_val[0] - (round(upper_bound, 6) * offset_val[1])
            else:
                timestamp = timestamp
            id_list[unique_id] = upper_bound



            self.logger.info("ID: {} \t  lower bound: {} \t  upper bound: {} ".format(unique_id,lower_bound,upper_bound ))
        return id_list
