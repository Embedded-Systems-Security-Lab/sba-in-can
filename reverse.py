from schedule_attack.reverse_engineer.reverse_log import ReverseLogs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, help="CSV file to reverse engineer", default='./OAK-old/Attack_free_dataset.csv')
parser.add_argument("--bus_speed", type=int, help="Bus speed", default=500000)
args = parser.parse_args()

def main():

    s = ReverseLogs(args.data, args.bus_speed)
    s.period_bounds()

if __name__ == "__main__":
    main()

