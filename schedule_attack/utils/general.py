import time
import random
import os
from functools import reduce
import fractions
import math
import csv


class General(object):
    """docstring for General"""

    STUFF_LEN = 5
    EPSILON = 0.00001
    HEADER_DATA_BYTE = 1024

    #First data sets

        # For the synthetic data
    HARMONIC_DATA = [(1,2,4,8,40,200,1000), (1, 5,10,20, 40, 200, 1000), (1, 5, 10,50,100,200,1000), (1, 5, 25, 50, 100, 200, 1000),\
    (1, 5, 25, 125, 250, 500, 1000), (1, 5, 10,50,100,500,1000), (1, 2, 10, 20, 40, 200, 1000), (1, 2, 10, 50, 100, 200, 1000),\
    (1,2,10,20,100,200,1000),(1, 5, 10, 20, 100,200, 1000), (1,2,10,20,100,500,1000), (1,5,10,20,100,500,1000), (1,5,25,50,100,500,1000),\
    (1,2,10,50,100,500,1000),(1,2,10,50,250,500,1000),(1,5,10,50,250,500,1000), (1, 5, 25, 50, 250, 500, 1000)]

    #Make the jitter constant fr particular ECU

    @staticmethod
    def change_period_output_file(name, num):
        return name + str(num) + ".csv"

    @staticmethod
    def generate_new_output_file_name(num):
        return time.strftime("%Y%m%d-%H%M%S") + "_" + str(num) + "_log.csv"

    @staticmethod
    def get_transmission_time(data_len, bus_speed, max_bit=55):

        assert (int(bus_speed) != 0), "Bus speed cannot be zero"

        return (max_bit + (10* int(data_len))) * (1/float(bus_speed))

    #To create a directory
    @staticmethod
    def check_and_make_directory(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

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
