from ..utils.general import *
from ..utils.logger import CustomLogger
from .message import *
import csv
import heapq
import random
import copy
import os
import sys


class Simulation(object):
    """docstring for Simulation"""

    # Contains message objects/jobs after instantiation
    pending_queue = []

    active_queue = []
    # message object/job enters transmission_queue after winning arbitration
    transmission_queue = []
    __PERIOD__PREFIX_NAME = "period_"
    __JITTER_RANDOM = 0.05
    __OFFSET_RANDOM = 100

    def __init__(self, seed, bus_speed, with_jitter=False, with_offset=False,log_file="sim_logger.log"):
        super(Simulation, self).__init__()
        random.seed(seed)
        self.bus_speed = bus_speed
        self.with_jitter = with_jitter
        self.with_offset = with_offset
        self.logger = CustomLogger(__name__,log_file)

    def job_init(self, output_dir, num_jobs,num,tag_num):

        if num >= len(General.HARMONIC_DATA):
            self.logger.error("index must be between 0 - 16")
            sys.exit()


        self.clear_heapq()

        period_file_path = General.change_period_output_file(Simulation.__PERIOD__PREFIX_NAME,tag_num)
        # Appends remaining output file directory to absolute path
        period_file_path = os.path.join(output_dir, period_file_path)
        # Creates given directory path if not already existing
        General.check_and_make_directory(period_file_path)

        # Opens period file and writes header data
        with open(period_file_path, "w") as output:
            writer = csv.writer(output, lineterminator = '\n')
            writer.writerow(["ID", "DLC", "Period", "Phase", "Jitter"])

            periods_data = []
            for x in range(num_jobs):
                try:
                    period = General.HARMONIC_DATA[num][random.randint(0,len(General.HARMONIC_DATA[num]) - 1)]
                except:
                    self.logger.error("Invalid index")
                    sys.exit()
                periods_data.append(period)
            periods_data.sort()
            for x in range(num_jobs):
                jitter = 0.0
                offset = 0
                if self.with_jitter:
                    jitter = random.uniform(Simulation.__JITTER_RANDOM)
                if self.with_offset:
                    offset = random.uniform(Simulation.__OFFSET_RANDOM)
                id, dlc,  = x+1, random.randint(1,8),
                transmission_time = General.get_transmission_time(dlc,self.bus_speed)
                data = ["{0:02x}".format(random.randint(0, 255)) for i in range(0, dlc)]
                new_job = SIMMessage(id, dlc, periods_data[x], transmission_time, data, offset, jitter=jitter)
                heapq.heappush(self.pending_queue, new_job)
                writer.writerow([hex(new_job.id), new_job.dlc, new_job.period,new_job.release_time, new_job.jitter])

        return period_file_path

    # Pops all jobs off of pending_queue heap
    def clear_heapq(self):
        while self.pending_queue:
            heapq.heappop(self.pending_queue)

    def calc_util(self):
        sum_util = 0
        sum_util = sum([self.pending_queue[i].transmission_time/self.pending_queue[i].period \
        for i in range(0, len(self.pending_queue))])
        self.logger.info("\nUtilization Um, is: {} ".format(sum_util))
        return sum_util

    """Convert pending to active job."""
    def convert_to_active_job(self, p_job):
        p_job.is_pending = False
        p_job.is_active = True
        return p_job

    def run_simulation(self, max_time=4000):
        finished_jobs = []
        delta = 1/(self.bus_speed * 100)
        r_time = 0.0
        while r_time < max_time:
            self.logger.debug("At t = {}".format(r_time))
            saved_jobs = []
            """+ self.pending_queue[0].jitter"""
            while self.pending_queue and (r_time - (self.pending_queue[0].release_time + self.pending_queue[0].jitter ))  > General.EPSILON:
                pending_jobs = heapq.heappop(self.pending_queue)
                saved_jobs.append(copy.deepcopy(pending_jobs))
                active_job = self.convert_to_active_job(pending_jobs)
                heapq.heappush(self.active_queue, (active_job))

            # Moves job from active queue to transmission queue and calculates end transmission time
            if self.active_queue and not self.transmission_queue:
                self.transmission_queue.append(heapq.heappop(self.active_queue))
                self.transmission_queue[0].end_transmission_time = r_time + \
                self.transmission_queue[0].transmission_time


            while self.transmission_queue and  r_time - self.transmission_queue[0].end_transmission_time > General.EPSILON:
                finished_jobs.append(self.transmission_queue.pop(0))

                if self.active_queue:
                    self.transmission_queue.append(heapq.heappop(self.active_queue))
                    self.transmission_queue[-1].end_transmission_time = r_time + \
                    self.transmission_queue[-1].transmission_time

            for job in saved_jobs:
                job.instance_no += 1
                job.release_time = job.offset + job.period * job.instance_no
                if self.with_jitter:
                    job.jitter = random.uniform(Simulation.__JITTER_RANDOM)
                heapq.heappush(self.pending_queue, job)
            r_time += delta #Best way to simulate the time

        # Free memory by deleting queues
        del self.transmission_queue[:]
        del self.pending_queue[:]
        del self.active_queue[:]
        del saved_jobs[:]

        return finished_jobs



if __name__ == '__main__':
    main()
