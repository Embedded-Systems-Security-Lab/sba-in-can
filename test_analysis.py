from schedule_attack.analysis.analysis import Analysis
from schedule_attack.utils.general import General
from schedule_attack.utils.optimization_type import Optimization
from schedule_attack.utils.logger import CustomLogger
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, help="CSV file to reverse engineer", default="OAK-old/tm4c-sae-125kbps-10m-reset-5.txt")
parser.add_argument("--bus_speed", type=int, help="Bus speed", default=125000)
parser.add_argument("--num_period_analyze", type=int, help="Number of hyperiods to analyze", default=10)
parser.add_argument("--num_periods_to_verify", type=int, help="Number of hyperiods to verify", default=50)
parser.add_argument("--type_of_opt", type=Optimization.from_string, help="Optimization type ", default=Optimization.NO_OPT)
parser.add_argument("--logger_name", type=str, help="Logger name to add logger", choices=list(Optimization), default="main_analysis_logger.log")
args = parser.parse_args()

logger = CustomLogger(__name__,args.logger_name)

def main():
    analysis = Analysis(args.num_period_analyze, args.data, args.bus_speed)
    analysis.get_pattern_instance_info()
    analysis.verify_target_times(args.num_periods_to_verify, args.num_period_analyze,args.type_of_opt)
    logger.debug("Finished Analysis")



if __name__ == '__main__':
    main()
