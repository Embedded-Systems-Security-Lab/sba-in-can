import time
import enum
import random
import os
from functools import reduce
import fractions
import math
import csv

class SIM_TYPE(enum.Enum):

    SAE_DATA = 1
    NEW = 2
    HARMONIC = 3


class General(object):
    """docstring for General"""


    STUFF_LEN = 5
    EPSILON = 0.0000001
    HEADER_DATA_BYTE = 1024

    #First data sets
    SAE_SIM_DATA = [ ("0XA0", 1, 5,ECU.V_C),("0XB0", 6, 10,ECU.V_C),("0XD0", 1, 1000,ECU.V_C),("0XA1", 2, 5,ECU.Brakes),("0XC1", 1, 100,ECU.Brakes), \
        ("0XB2", 1, 10,ECU.Battery),("0XC2", 4, 100,ECU.Battery),("0XD2", 3, 1000,ECU.Battery),("0XA3", 1, 5,ECU.Driver),("0XB3", 2, 10,ECU.Driver),("0XA4", 2, 5,ECU.I_M),\
        ("0XB4", 2, 10,ECU.I_M),("0XA5", 1, 5,ECU.Trans),("0XC5", 1, 100,ECU.Trans),("0XD5", 1, 1000,ECU.Trans)]

        # For the synthetic data
    HARMONIC_DATA = [(1,2,4,8,40,200,1000,), (1, 5,10,20, 40, 200, 1000), (1, 5, 10,50,100,200,1000), (1, 5, 25, 50, 100, 200, 1000),\
    (1, 5, 25, 125, 250, 500, 1000), (1, 5, 10,50,100,500,1000), (1, 2, 10, 20, 40, 200, 1000), (1, 2, 10, 50, 100, 200, 1000),\
    (1,2,10,20,100,200,1000),(1, 5, 10, 20, 100,200, 1000), (1,2,10,20,100,500,1000), (1,5,10,20,100,500,1000), (1,5,25,50,100,500,1000),\
    (1,2,10,50,100,500,1000),(1,2,10,50,250,500,1000),(1,5,10,50,250,500,1000), (1, 5, 25, 50, 250, 500, 1000)]

    #Make the jitter constant fr particular ECU
    jitter_ecu = {
        ECU.Battery: random.uniform(0.1, 1.2),
        ECU.Driver : random.uniform(0.1,0.9),
        ECU.Brakes : random.uniform(0.1,0.4),
        ECU.Trans : random.uniform(0.1,0.3),
        ECU.V_C : random.uniform(0.1,1.7),
        ECU.I_M : 0.1
    }



    @staticmethod
    def change_period_output_file(name, num,num_2=None):
        if num_2 == None:
            return name+ str(num) + ".csv"
        return name + str(num) + "_" + str(num_2) + ".csv"

    #,(43,8,5,ECU.I_M),(49,8,5,ECU.I_M)]
    @staticmethod
    def get_random_val(start,end):
        return random.uniform(start,end)

    @staticmethod
    def generate_new_output_file_name(num):
        return time.strftime("%Y%m%d-%H%M%S") + "_" + str(num) + "_log.csv"

    @staticmethod
    def get_transmission_time(data_len, bus_speed, max_bit=55, stuff=0):

        assert (int(bus_speed) != 0), "Bus speed cannot be zero"

        return (max_bit + stuff + (8* int(data_len))) * (1/float(bus_speed))

    #To create a directory
    @staticmethod
    def check_and_make_directory(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_dataset(data_type):

        if data_type == "HARMONIC":
            return General.HARMONIC_DATA
        elif data_type == "SAE_DATA_1":
            return General.SAE_SIM_DATA_1
        elif data_type ==  "SAE_DATA_2":
            return General.SAE_SIM_DATA_2
        elif data_type == "RANDOM" or data_type == "CUSTOM":
            lst = [None] * 15
            return lst
        return 0

    @staticmethod
    def lcm(denominators):
        denominators = [math.ceil(val) for val in denominators]
        return reduce(lambda a,b: a*b//math.gcd(a,b), denominators)

    @staticmethod
    def log_to_csv(output_dir, job_list, num):
        csv_file = General.generate_new_output_file_name(num)
        csv_file_path = os.path.join(output_dir, csv_file)
        General.check_and_make_directory(csv_file_path)

        # Writes data to csv file
        with open(csv_file_path, "w") as output:
            writer = csv.writer(output, lineterminator = '\n')
            writer.writerow(["ID", "DLC", "DATA", "TIMESTAMP", "Release Time", "Period", "Jitter"])
            for val in job_list:
                list_val = list(val)
                list_val[0] = hex(list_val[0])
                writer.writerow(list_val)
        return csv_file_path

    @staticmethod
    def log_dict_to_csv(output_file_csv, dict_data, csv_columns=None):
        with open(output_file_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
