from schedule_attack.simulation.simulation import *
from schedule_attack.utils.general import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, help="Random seed for the simulation", default=0x1234AB)
parser.add_argument("--num_jobs", type=int, help="Number of distinct PIDs to simulate", default=10)
parser.add_argument("--num_runs", type=int, help="Running the first simulation from file", default=2)
parser.add_argument("--sim_time", type=int, help="Running the first simulation from file", default=10)
parser.add_argument("--name_tag", type=str, help="Tag to insert in output filenames", default="default")
args = parser.parse_args()

def main():

    if args.num_jobs <= 0:
        print('At least 1 job is required!')
        sys.exit(1)
    max_tryout = 10_000
    sim = Simulation(args.seed, bus_speed=500)
    csv_folder = "data"
    for index in range(len(General.HARMONIC_DATA)):
        for num in range(args.num_runs):
            sum_util = 100
            tryout = 0
            while ((sum_util < 0.5) or (sum_util > 1.0)) and (tryout < max_tryout):
                sim.clear_heapq()
                # TODO: embed a useful tag in the file names
                tag_num = index*args.num_runs + num
                period_file = sim.job_init(
                        csv_folder,
                        args.num_jobs,
                        index,
                        tag_num)

                tryout += 1
                sum_util = sim.calc_util()
                if tryout == max_tryout and ((sum_util < 0.5) or (sum_util > 1.0)):
                    print("Not Schedulableafter trying {} times".format(tryout))
                    sys.exit()
            job_list = sim.run_simulation(args.sim_time)
            # TODO: embed a useful tag in the file names
            file_name = General.log_to_csv(
                    csv_folder,
                    job_list,
                    num=str(tag_num) + "-" + str(round(sum_util, 4)))
            del job_list[:]


if __name__ == '__main__':
    main()
