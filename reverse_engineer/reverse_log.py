import os
import csv
import math
import sys


class ReverseLogs(object):

    def __init__(self, log_list=[]):
        super(ReverseLogs, self).__init__()
        #self.log_list = log_list


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

    def period_bounds(self,bus_speed):
        if not self.log_list:
            print("The log list is empty")
            return

        unique_ids = list(set({log.id for log in self.log_list}))
        unique_ids.sort()
        timestamp = 0
        dlc = 0
        phase = 0

        #id_list = []
        id_list = {}
        unique_id_vars = {}


        """Iterate through the unique ids to find the lower and upper bound"""
        for unique_id in unique_ids:
            instance_of_unique_id = 1
            upper_bound = 10000
            lower_bound = -1
            delta = 1/General.BUS_SPEED
            got_offset = False
            offset_val = None


            for i in range(len(self.log_list)):
                lower = -1
                upper = 1000
                if unique_id == self.log_list[i].id :
                    #print i
                    #self.unique_ids_with_period.setdefault(unique_id, {"timestamp": [], "new_timestamp": []})["timestamp"].append(self.log_list[i].timestamp)
                    if instance_of_unique_id > 1:
                        lower_id = i - 1
                        while lower_id >= 0:

                            # if abs(int(self.log_list[lower_id].id)) == abs(int(self.log_list[i].id)):
                            #   lower_id = -1
                            #   break
                            # if float(self.log_list[lower_id+1].timestamp) - float(self.log_list[lower_id].timestamp) \
                            #   - float(self.log_list[lower_id+1].transmission_time) > General.EPSILON:
                            #   lower_id = lower_id + 1
                            #   break
                            if abs(int(self.log_list[lower_id].id)) < abs(int(self.log_list[i].id)):
                                lower_id -= 1
                            else:
                                break

                        if (lower_id <= 0):
                            continue
                        #print(self.log_list[i].timestamp, self.log_list[i].transmission_time, self.log_list[i-1].timestamp, self.log_list[i].timestamp - self.log_list[i].transmission_time)
                        if not got_offset and ((self.log_list[i].timestamp - self.log_list[i].transmission_time) > (self.log_list[i-1].timestamp + 0/General.BUS_SPEED)):#+ 3/General.BUS_SPEED
                            #print(self.log_list[i].timestamp - self.log_list[i].transmission_time, self.log_list[i-1].timestamp, self.log_list[i-1].timestamp + 0/General.BUS_SPEED)
                            offset_val = (self.log_list[i].timestamp - self.log_list[i].transmission_time, instance_of_unique_id-1)
                            #print(offset_val)
                            #print(offset_val, hex(unique_id), self.log_list[i].timestamp, self.log_list[i].transmission_time, instance_of_unique_id)
                            got_offset = True

                        timestamp_offset = float(self.log_list[lower_id].timestamp) - timestamp
                        timestamp_offset_1 = float(self.log_list[i].timestamp) - timestamp
                        lower = abs(timestamp_offset - self.log_list[lower_id].transmission_time)/(instance_of_unique_id - 1)
                        upper = abs(timestamp_offset_1 - (self.log_list[i].transmission_time))/(instance_of_unique_id - 1)
                    else:
                        timestamp = self.log_list[i].timestamp - self.log_list[i].transmission_time
                        dlc = self.log_list[i].dlc
                        data = self.log_list[i].data
                        #cp = self.log_list[i].transmission_time
                        #print(cp, timestamp)
                    if (abs(upper - lower ) < delta):
                        lower_bound = lower
                        upper_bound = upper
                        instance_of_unique_id += 1
                        delta = abs(upper - lower )
                        break

                    instance_of_unique_id += 1
                    if (round((lower + General.TOLERANCE),5) < round(lower_bound,5)) or (round(upper,5) > round((upper_bound + General.TOLERANCE),5)):
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

            #self.unique_ids_with_period[unique_id]["period"] = round(upper_bound, 6)


            print ("ID: " +str(unique_id)+"\t [" +  str(lower_bound) + "," + str(upper_bound) + "]" + "\t" + str(timestamp))
        return id_list
