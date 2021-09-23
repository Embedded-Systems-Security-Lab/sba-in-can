from schedule_attack.analysis.analysis_old import Analysis
from schedule_attack.utils.general import General
from schedule_attack.utils.optimization_type import Optimization
from schedule_attack.utils.logger import CustomLogger
import argparse



def main():
    num_of_periods_to_verify = 50
    num_of_periods_to_analyze = 10
    analysis = Analysis(10, "OAK-old/tm4c-sae-125kbps-10m-reset-5.txt", 125000)
    analysis.get_pattern_instance_info()
    analysis.verify_target_times(num_of_periods_to_verify, num_of_periods_to_analyze,Optimization.NO_OPT)


if __name__ == '__main__':
    main()
