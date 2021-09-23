import re
from .general import *


class ProcessFile(object):

    @staticmethod
    def process_oak_2020_data(path, separators_list, bus_speed):

        res = []
        regular_exp = '|'.join(map(re.escape, separators_list))
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                line = re.split(regular_exp, line)
                ID, DLC, DATA, timestamp = line[4], 8, line[5], float(line[1])
                transmission_time = General.get_transmission_time(DLC,bus_speed)
                res.append((ID, DLC, DATA, timestamp, transmission_time))

        return res

    @staticmethod
    def process_oak_old_data(path, bus_speed):
        res = []
        with open(path, "r") as file:
            has_header = csv.Sniffer().has_header(file.read(General.HEADER_DATA_BYTE))
            file.seek(0)
            reader = csv.reader(file)
            if has_header:
                next(reader)
            for row in reader:
                ID, DLC, DATA, timestamp = row[0], int(row[1]), row[2], float(row[3])

                transmission_time = General.get_transmission_time(DLC,bus_speed)
                res.append((ID, DLC, DATA, timestamp, transmission_time))

        return res

    @staticmethod
    def process_sae_data(path, bus_speed):
        res = []
        with open(path, 'r') as file:
            for index, line in enumerate(file):

                if index == 0:
                    continue
                line.rstrip()
                line = line.split(',')
                dlc = line[-4]
                data = line[-3]
                try:
                    dlc = int(dlc.strip("'"))
                except:
                    print('cant')
                ID, DLC, DATA, timestamp = int(line[3].strip("'")), dlc, data, float(line[0])
                transmission_time = General.get_transmission_time(DLC,bus_speed)
                res.append((ID, DLC, DATA, timestamp, transmission_time))

        return res
