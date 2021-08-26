from .reverse_engineer.reverse_logs import ReverseLogs

def main():

    s = ReverseLogs()

    s.period_bounds("../temp/20210505-160928_0_log.csv")


if __name__ == "__main__":

    main()

