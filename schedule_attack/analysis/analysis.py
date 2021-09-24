# The purpose of this code is to implement the AwSM attack.

import csv
import json
import os
import sys
import time
#from posix import times_result
from ..utils.process_file import ProcessFile
from ..reverse_engineer.reverse_log import ReverseLogs
from ..utils.general import General
from ..utils.logger import CustomLogger
from ..utils.optimization_type import Optimization


class Analysis(object):

    def __init__(self, num_of_hyperperiods, file_name, bus_speed,log_file="analysis_logger.log"):

        self.logger = CustomLogger(__name__,log_file)
        #self.hyperperiod = 1.009745 # Manual inspection
        self.hyperperiod = 1.000023 # Manual inspection for sae datasets
        self.reset(num_of_hyperperiods, file_name, bus_speed)



    def reset(self, num_of_hyperperiods, file_name, bus_speed):
        self.num_of_hyperperiods = num_of_hyperperiods
        self.file_name = file_name
        self.bus_speed = bus_speed
        #self.total_hyperiod = self.hyperperiod * num_of_hyperperiods
        self.ifs = 3/self.bus_speed
        self.get_entire_ids()
        self.get_number_of_message()

    def get_entire_ids(self):
        self.data = ProcessFile.process_sae_data(self.file_name, self.bus_speed)
        self.entire_set_of_IDs = set([msg[0] for msg in self.data if msg[0] != 1]) # Manually removing 1 for the sae datasets

    def get_pattern_instance_info(self):

        self.patterns = {}

        for victim_ID in self.entire_set_of_IDs:
            self.patterns.setdefault(victim_ID, {})
            prev_msg_time = -1
            self.patterns[victim_ID]
            for i in range(self.num_of_hyperperiods):
                prev_msg_time, pat= self.identify_patterns(i, prev_msg_time, int(victim_ID))
                self.logger.info(prev_msg_time)
                self.logger.info(pat)
                self.patterns[victim_ID].setdefault(i, pat)
        self.logger.debug("All patterns is {}".format(self.patterns))


    def calculate_hyperperiod(self):
        """
            Round off error of hyperperiod = 2.0 but with manual inspection, hyperperiod = 1.009745

        """
        r = ReverseLogs(self.file_name, self.bus_speed) #Using bus_speed of 500kbs
        r_info = r.period_bounds()
        keys = [key for key in r_info if key != 1]
        periods = [r_info[key] for key in keys if key != 1]
        hyperperiod = General.lcm(periods)
        self.logger.debug("Hyperperiod is: {} ".format(hyperperiod))


    def get_number_of_message(self):

        self.hyperperiod_list = General.get_hyperperiod_list(self.data, self.hyperperiod)
        self.one_hyperperiod_len = len(self.hyperperiod_list)
        self.total_hyperperiod_len = self.one_hyperperiod_len * self.num_of_hyperperiods
        self.total_hyperperiod_list = General.get_hyperperiod_list_len(self.data, self.total_hyperperiod_len)
        self.logger.debug("len of Hyperperiod is: {} ".format(len(self.hyperperiod_list)))
        self.logger.debug("len of total Hyperperiod is: {} ".format(len(self.total_hyperperiod_list)))

    def identify_patterns(self, current_hyperperiod, prior_msg_t, target_msg):
        msg_count = current_hyperperiod * self.one_hyperperiod_len
        prev_msg_count = msg_count
        period_limit = (current_hyperperiod+1) * self.one_hyperperiod_len
        l_time, h_time = 0, 0
        l_pat, h_pat = [0], [0]
        targ_msg_instance = 0

        pat = []

        while msg_count < self.total_hyperperiod_len and msg_count < period_limit:
            msg_ID, dlc, _, msg_timestamp, msg_tx_time = self.total_hyperperiod_list[msg_count]
            if (int(msg_ID) == target_msg):
                targ_msg_instance += 1

            # Calculate msg start time
            msg_start_time = msg_timestamp - msg_tx_time

            # Calculate msg midpoint
            msg_midpoint = msg_timestamp - (msg_tx_time/2)

            # Calculate time between current message and previous message
            time_diff = (msg_start_time - prior_msg_t)

            if time_diff > self.ifs:
                l_time, h_time = 0, 0
                l_sequence, h_sequence = [], [] # Stores sequence of IDs just before target, includes target as well

                #check if message is target message
                if (int(msg_ID) == target_msg):
                    prev_msg = None

                    pat.append(
                        [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                        msg_midpoint, msg_timestamp, msg_tx_time]
                        )
                    prev_msg = msg_ID

            elif (int(msg_ID) > target_msg):

                l_time = msg_timestamp
                h_time = 0
                h_sequence = []

                prev_msg = msg_ID

            elif (int(msg_ID) == target_msg):

                if l_time > 0:

                    pat.append(
                        [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                        msg_midpoint, l_time, msg_tx_time]
                        )
                elif h_time > 0:

                    pat.append(
                        [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                        msg_midpoint, h_time, msg_tx_time]
                        )

            elif int(msg_ID) < target_msg:

                if h_time == 0:
                    h_time = msg_timestamp
                    l_time = 0
                    l_sequence = []
                    prev_msg = msg_ID
                else:
                    prev_msg = msg_ID

            prior_msg_t = msg_timestamp

            msg_count += 1
        self.logger.debug("Number of msg_count is {} and id: {}".format(msg_count - prev_msg_count, target_msg))
        return prior_msg_t, pat


    def verify_target_times(self, num_of_periods_to_check, num_of_periods_analyzed, optimization_method=Optimization.AVERAGE_START_TIME):

        if not self.patterns:
            self.logger.warn("Obtain pattern before calling this function")
            sys.exit()

        period = 1
        num_of_periods_to_check += 1 # need to increase this so that the number line up

        for id in self.patterns:
            self.logger.debug("Processing message ID: {}".format(id))
            num_of_patterns_found_in_first_period = len(self.patterns[id][0])

            if optimization_method == Optimization.NO_OPT:
                self.logger.debug('Using time of previous msg + period method (Method #1).  No optimizations.')
                u = 0
                while u < num_of_patterns_found_in_first_period:
                    self.logger.debug(u)
                    self.patterns[id][0][u][5] += 1
                    u += 1

            elif optimization_method == Optimization.AVERAGE_START_TIME:
                self.logger.debug('Performing average start time method (Method #2) for optimization.')
                for j in range(len(self.patterns[id][0])):
                    sum = 0
                    count = 0
                    average = 0
                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i]:
                            if self.patterns[id][i][j][1] != None:
                                sum += self.patterns[id][i][j][3] - (period*i)
                                count += 1
                    if count != 0:
                        average = sum/count

                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i] and self.patterns[id][i][j][1] != None:
                            self.patterns[id][i][j][5] = average + (period*(i+1))

            elif optimization_method == Optimization.INTERSECTION:
                self.logger.debug('Performing intersection method (Method #3) for optimization')
                # u = 1

                for j in range(len(self.patterns[id][0])):
                    max_time = None
                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i] and self.patterns[id][i][j][1] != None:
                            current_time = (self.patterns[id][i][j][3] - (period*i))
                            if max_time == None or current_time > max_time:
                                max_time = current_time

                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i] and self.patterns[id][i][j][1] != None and max_time != None:
                            self.patterns[id][i][j][5] = max_time + (period*(i+1))

            elif optimization_method == Optimization.AVERAGE_MID_TRANS:
                self.logger.debug('\nPerforming average midpoint time method (Method #4) for optimization\n')

                for j in range(len(self.patterns[id][0])):
                    sum = 0
                    count = 0
                    average = 0
                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i] and self.patterns[id][i][j][1] != None:
                            sum += self.patterns[id][i][j][4] - (period*i)
                            count += 1
                    if count != 0:
                        average = sum/count

                    for i in range(self.num_of_hyperperiods):
                        if self.patterns[id][i] and self.patterns[id][i][j][1] != None and count != 0:
                            self.patterns[id][i][j][5] = average + (period*(i+1))

            else:
                self.logger.error("Unrecognized type {}".format(optimization_method))
                sys.exit()

            pattern_num = 1
            for times_and_seqs in self.patterns[id][0]:

                next_prev_msg_time = times_and_seqs[5]
                prev_msg = times_and_seqs[1]
                target_msg = times_and_seqs[2]
                time_stamp = 0
                hit_counter = 0
                targ_instance_num = times_and_seqs[0]


                if prev_msg == None:
                    self.logger.debug('skipping ahead due to idle count')
                    continue
                idx = 0

                p = 2
                while p < num_of_periods_to_check + num_of_periods_analyzed:


                    while time_stamp < next_prev_msg_time:
                        ID_field, dlc, _ ,time_stamp, tx_time = self.data[idx]
                        idx += 1
                    if prev_msg == ID_field:
                        next_prev_msg_start = time_stamp - tx_time
                        if next_prev_msg_start <= next_prev_msg_time <= float(time_stamp):
                            ID_field, dlc, _ ,time_stamp, tx_time = self.data[idx]
                            idx += 1
                            if target_msg == ID_field:
                                if p > (num_of_periods_analyzed + 2):
                                    self.logger.debug('Verified {} {} sequence hit at {} in period {}'.format(prev_msg,target_msg,next_prev_msg_time,p))
                                    hit_counter += 1

                # Determine next time message prior to target is expected
                    next_prev_msg_time += period
                    p += 1
                    if idx >= len(self.data):
                        self.logger.debug("Finished processing the data")
                        break


                self.logger.debug("total hits for instance # {} of  {} pattern # {},  {} \
                     is {} {}".format(targ_instance_num,target_msg,pattern_num, \
                        times_and_seqs[1],hit_counter,num_of_periods_to_check-1))


                pattern_num += 1
