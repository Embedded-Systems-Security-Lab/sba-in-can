from schedule_attack.reverse_engineer.reverse_log import ReverseLogs

def main():

    #s = ReverseLogs("data/20210826-173253_0-0.6233_log.csv", 500)
    s = ReverseLogs('./OAK-old/Attack_free_dataset.csv', 500000)

    s.period_bounds()

if __name__ == "__main__":

    main()

