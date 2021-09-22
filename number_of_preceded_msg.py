from schedule_attack.utils.process_file import *
from schedule_attack.reverse_engineer.reverse_log import ReverseLogs
from schedule_attack.utils.general import *
from schedule_attack.utils.logger import CustomLogger
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, help="CSV file to reverse engineer", default='./OAK-old/Attack_free_dataset.csv')
parser.add_argument("--logger_name", type=str, help="Logger name to log data", default="preceded_logger.log")
parser.add_argument("--bus_speed", type=int, help="Bus speed", default=500000)
parser.add_argument("--num_period", type=int, help="Number of Hyperperiod to Evaluate", default=1)

args = parser.parse_args()

logger = CustomLogger(__name__,args.logger_name)



def main():

    r = ReverseLogs(args.data, args.bus_speed) #Using bus_speed of 500kbs
    r_info = r.period_bounds()
    data = ProcessFile.process_oak_old_data(args.data, args.bus_speed)
    keys = [key for key in r_info if key != 1]
    periods = [r_info[key] for key in keys if key != 1]

    hyperperiod = General.lcm(periods)
    logger.debug("Hyperperiod is: {} ".format(hyperperiod)) # Round off error from floating number
    # Using manual inspection
    hyperperiod = 1.009745
    #hyperperiod = 1
    sequence = args.num_period * hyperperiod

    sequence_list = General.get_hyperperiod_list(data, sequence)

    logger.debug("The sequence list are {}".format(sequence_list))

    result = General.get_preceded_id(sequence_list)

    num_res = {}

    for key in result:
        count = len(result[key])
        if count in num_res:
            num_res[count] += 1
        else:
            num_res[count] = 1

    logger.debug("With {} number of hyperpeiod, the results are {}".format(args.num_period,num_res))
    sum = 0
    for key in num_res:
        sum += num_res[key]
        logger.debug("{} message id has {} number of preceded ID".format(num_res[key],key))
    logger.debug("There is {} total number of messages".format(sum))

if __name__ == "__main__":

    main()
