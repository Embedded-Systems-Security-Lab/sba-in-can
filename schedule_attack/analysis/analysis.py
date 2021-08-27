# The purpose of this code is to implement the AwSM attack.

import csv
import json
import os
from posix import times_result


def get_num_of_files(filenames):
    """Determine number of files listed in a file."""
    stream3 = open(filenames)
    file_count = 0

    for line in stream3:
        file_count += 1

    stream3.close()
    return file_count


def get_next_schedule_info(csv_reader2):
    """Obtain information specific to the next schedule being read"""
    line = next(csv_reader2)
    filename = line[0]
    bus_speed = line[1]
    num_messages_in_period = line[2]
    total_lines = line[3] # may not be needed anymore
    print('\n\nProcessing schedule', filename, '...')

    return filename, int(bus_speed), int(num_messages_in_period)


def get_next_msg_info(csv_reader):
    """Obtain ID of next message from the file/bus"""
    next_msg = next(csv_reader)
    ID_field = next_msg[3]
    time_stamp = next_msg[0]
    dlc = next_msg[4]

    return ID_field, time_stamp, dlc


def get_tx_times_and_ifs(bus_speed):

    # Tx_times (below) based on the following bit counts.
    #
    # Format: {'dlc' : bit_count, .... }
    # {'0' : 44, '1' : 52,  '2' : 60,
    #  '3' : 68, '4' : 76,  '5' : 84,
    #  '6' : 92, '7' : 100, '8' : 108}
    #
    # ifs is 3/speed

    if bus_speed == 125000:
        ifs = 0.000024
        tx_times = {
            '0' : 0.000352, '1' : 0.000416, '2' : 0.000480,
            '3' : 0.000544, '4' : 0.000608, '5' : 0.000672,
            '6' : 0.000736, '7' : 0.000800, '8' : 0.000864
        }

    else: # Bus speed == 500000
        ifs = .000006
        tx_times = {
            '0' : 0.000088, '1' : 0.000104, '2' : 0.00012,
            '3' : 0.000136, '4' : 0.000152, '5' : 0.000168,
            '6' : 0.000184, '7' : 0.0002,   '8' : 0.000216
        }

    return tx_times, ifs


def identify_patterns(stream, hyperperiod_msg_count, prior_msg_t,
                      target_msg, hyperprd_time, bus_speed):
    """Identify patterns for AwSM attack"""

    msg_count = 0
    l_time, h_time = 0, 0
    tx_times, ifs = get_tx_times_and_ifs(bus_speed)
    sequence_set = set() # holds set of IDs that preceded target ID
    targ_msg_instance = 0
    pat = [] # this will hold all patterns and related information

    while msg_count < hyperperiod_msg_count:

        msg_ID, msg_time, dlc = get_next_msg_info(stream)

        if (int(msg_ID) == target_msg):
            targ_msg_instance += 1

        # Convert timestamp to float
        msg_timestamp = float(msg_time)

        # Calculate msg transmisison time
        msg_tx_time = tx_times[str(dlc)]

        # Calculate msg start time
        msg_start_time = msg_timestamp - msg_tx_time

        # Calculate msg midpoint
        msg_midpoint = msg_timestamp - (msg_tx_time/2)

        # Calculate time between current message and previous message
        time_diff = (msg_start_time - float(prior_msg_t))

        # If time difference is more than IFS, there was idle time.
        if time_diff > ifs:
            l_time, h_time = 0, 0

            #check if message is target message
            if int(msg_ID) == target_msg:
                prev_msg = '2049'
                #print('target', target_msg,  'came after idle time')
                #print('prev_msg var set to ', prev_msg)

                pat.append(
                    [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                    msg_midpoint, msg_timestamp, msg_tx_time])

                prev_msg = msg_ID

        # If message obtained is of lower priority than target message
        elif int(msg_ID) > target_msg:
            l_time = float(msg_time)
            h_time = 0

            prev_msg = msg_ID

        # If message obtained is the target message, record previous
        # message ID or make note if there is idle time.
        elif int(msg_ID) == target_msg:
            if l_time > 0:
                sequence_set.add(prev_msg)

                pat.append(
                    [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                    msg_midpoint, l_time, msg_tx_time]
                    )

            elif h_time > 0:
                sequence_set.add(prev_msg)

                pat.append(
                    [targ_msg_instance, prev_msg, msg_ID, msg_start_time,
                    msg_midpoint, h_time, msg_tx_time]
                    )

        elif int(msg_ID) < target_msg:
            if h_time == 0:
                h_time = float(msg_time)
                l_time = 0
                prev_msg = msg_ID
            else:
                prev_msg = msg_ID

        prior_msg_t = msg_time
        msg_count += 1

    return prior_msg_t, sequence_set, pat


def get_pattern_instance_info(num_of_hyperperiods, schedules_and_info,
                              sched_dir, destination_dir):

    num_of_files = get_num_of_files(schedules_and_info)

    entire_set_of_IDs = {
        '165', '197', '163', '179',
        '161', '176', '160', '164',
        '180', '194', '210', '178',
        '193', '208', '213'
    }

    stream2 = open(schedules_and_info)
    csv_reader2 = csv.reader(stream2, delimiter=',', quotechar="'")

    f = 0
    while f < num_of_files:

        # Obtain information associated with next schedule to be read
        filename, speed, msg_per_hyperperiod = \
            get_next_schedule_info(csv_reader2)

        hyperperiod_time = 1.0

        # Check for patterns for all expected victim IDs.
        for victim_ID in entire_set_of_IDs:

            prev_msg_time = -1
            patterns = []

            can_bus = sched_dir + filename

            # Open schedule and remove column headers row
            stream = open(can_bus)
            csv_reader = csv.reader(stream, delimiter=',', quotechar="'")
            get_next_msg_info(csv_reader)


            # Identify patterns
            j = 0
            while j < num_of_hyperperiods:

                prev_msg_time, prev_msg_set, pat = identify_patterns(
                    csv_reader, msg_per_hyperperiod,
                    prev_msg_time, int(victim_ID), hyperperiod_time,
                    speed)

                j += 1


                if pat != []:
                    patterns.append([j, filename, speed, pat])

                # This was used to determine if there was an ID that
                # had multiple preceeding messages that could be used
                # for the AwSM attack. Likely can be removed.
                #if prev_msg_set != set():
                #    print('The set of previous messages for victim ID',
                #          victim_ID,'in period', j ,'is', prev_msg_set)

            stream.close()

            # Create json file if patterns were found for the victim ID
            if patterns != []:
                new_filename = filename[:-4] + '_' + str(victim_ID) \
                               + '_all_patterns.json'

                with open(destination_dir + new_filename, "w") as write_file:
                    json.dump(patterns, write_file)
        f += 1
    print('\n...target time/pattern identification complete.\n')


def obtain_json_filenames(json_dir):
    """Obtain the list of filenames ending in .json"""
    json_files = []
    for f_name in os.listdir(json_dir):
        if f_name.endswith('.json'):
            json_files.append(f_name)
    return json_files


def delete_json_files(json_dir):
    """Delete previous json files to prevent future iterations from \
        reading them."""

    json_files = []
    for f_name in os.listdir(json_dir):
        if f_name.endswith('.json'):
            json_files.append(f_name)

    for filename in json_files:
        os.remove(json_dir + filename)

    #print('json files removed.\n')
    return


def verify_target_times(num_of_h_periods_to_check, num_of_periods_analyzed,
                        json_dir, sched_dir, optimization_method = 1):
    """Idenfity when the predicted target time will actually hit target."""

    filenames = obtain_json_filenames(json_dir)
    h_period_time = 1
    num_of_h_periods_to_check += 1 #increase this so numbers line up

    for filename in filenames:
        with open(json_dir + filename) as json_file:
            data = json.load(json_file)

            #print(data[0][3][0][0]) # targ_msg_instance
            #print(data[0][3][0][1]) # prev_msg
            #print(data[0][3][0][2]) # msg_ID
            #print(data[0][3][0][3]) # msg_start_time
            #print(data[0][3][0][4]) # msg_midpoint
            #print(data[0][3][0][5]) # prev_msg_time
            #print(data[0][3][0][6]) # msg_tx_time

            sched_filename = data[0][1]
            print('using', sched_filename, 'for', data[0][3][0][2] )
            print('length of len(data) is', len(data))

            bus_speed = data[0][2]
            tx_times, ifs = get_tx_times_and_ifs(bus_speed)
            num_of_patterns_found_in_first_period = (len(data[0][3]))

            if optimization_method == 0:
                print('\nUsing time of previous msg + hyperperiod time '
                      'method (Method #1).  No optimizations.\n')
                u = 0  # instance number
                while u < num_of_patterns_found_in_first_period:
                    # Add hyperperiod time to prev message timestamp
                    data[0][3][u][5] += h_period_time
                    u += 1

            elif optimization_method == 1:
                print('\nPerforming average start time method (Method #2) '
                      'for optimization\n')

                # Obtain average of all start times
                for j in range(len(data[0][3])):
                    sum = 0
                    count = 0
                    average_start_time = 0

                    for i in range(len(data)):
                        if data[i][3][j][1] != '2049':
                            sum += data[i][3][j][3] - (h_period_time*i)
                            count += 1

                    if count != 0:
                        average_start_time = sum/count

                    #Update the values
                    for i in range(len(data)):
                        if data[i][3][j][1] != '2049':
                            data[i][3][j][5] = (average_start_time
                                                + (h_period_time*(i+1)))

            elif optimization_method == 2:
                print('\nPerforming intersection method (Method #3) for '
                      'optimization\n')

                # Obtain latest of all start times
                for j in range(len(data[0][3])):
                    latest_start_time = None
                    for i in range(len(data)):

                        if data[i][3][j][1] != '2049':
                            current_time = (data[i][3][j][3]
                                            - (h_period_time*i))

                            if latest_start_time == (
                                            None or
                                            current_time > latest_start_time
                                            ):
                                latest_start_time = current_time

                    # Replace all times associated with the same
                    # instance number of the the victim with the
                    # updated time
                    for i in range(len(data)):
                        if (data[i][3][j][1] != '2049' and
                                latest_start_time != None):
                            data[i][3][j][5] = (latest_start_time
                                                + (h_period_time*(i+1)))

            elif optimization_method == 3:
                print('\nPerforming average midpoint time method (Method #4)'
                      ' for optimization\n')

                for j in range(len(data[0][3])):
                    sum = 0
                    count = 0
                    average_midpoint = 0
                    for i in range(len(data)):

                        if data[i][3][j][1] != '2049':
                            sum += data[i][3][j][4] - (h_period_time*i)
                            count += 1
                    if count != 0:
                        average_midpoint = sum/count

                    #Update the values

                    for i in range(len(data)):
                        if data[i][3][j][1] != '2049' and count != 0:
                            data[i][3][j][5] = (average_midpoint
                                                + (h_period_time*(i+1)))

            pattern_num = 1 # Counter for keeping track of patterns
                            # for when they need to be referenced
                            # directly

            # Iterate through and verify all times after removing
            # filename entry
            for times_and_seqs in data[0][3]:
                #print(times_and_seqs)
                next_prev_msg_time = times_and_seqs[5]
                prev_msg = times_and_seqs[1]
                target_msg = times_and_seqs[2]
                time_stamp = 0
                hit_counter = 0
                targ_instance_num = times_and_seqs[0]

                if prev_msg == '2049':
                #    print('skipping ahead due to idle count')
                    continue

                # Open file and remove column headers row
                stream = open(sched_dir + sched_filename)
                csv_reader = csv.reader(stream, delimiter=',', quotechar="'")
                get_next_msg_info(csv_reader)

                p = 2
                while p < num_of_h_periods_to_check + num_of_periods_analyzed:

                    # Read schedule until time of the next iteration
                    # of message prior to target is reached
                    while float(time_stamp) < next_prev_msg_time:
                        ID_field, time_stamp, dlc = (
                                                get_next_msg_info(csv_reader)
                                                )

                    # Determine if target time has hit the next iteration
                    # of the msg prior to target
                    if prev_msg == ID_field:
                        next_prev_msg_start = (float(time_stamp)
                                               - tx_times[str(dlc)])
                        if (next_prev_msg_start
                            <= next_prev_msg_time
                            <= float(time_stamp)):
                            ID_field, time_stamp, dlc = (
                                                get_next_msg_info(csv_reader)
                                                )
                            if target_msg == ID_field:
                                if p > (num_of_periods_analyzed + 2):
                                    #print('Verified', prev_msg, target_msg,
                                    #      'sequence hit at',
                                    #      next_prev_msg_time,
                                    #      'in period', p)

                                    #print('Hit occurred', (next_prev_msg_time
                                    #    - next_prev_msg_start), 'seconds after'
                                    #    'start of transmission')
                                    hit_counter += 1
                            else:
                                pass
                                #print('prev_msg was followed by', ID_field,
                                #      'not', target_msg, 'in hyperperiod', p)
                        else:
                            pass
                            #print('Missed next iteration of prev message (',
                            #    prev_msg, ')' 'in hyperperiod', p)
                    else:
                        pass
                        #print('Recieve message', ID_field, 'does not match '
                        #    'prev_msg of', prev_msg, 'in hyperperiod', p )

                    # Determine next time message prior to target is expected
                    next_prev_msg_time += h_period_time
                    #print('period', p)
                    p += 1

                print('total hits for instance #', targ_instance_num, 'of ',
                      target_msg, '(pattern #', pattern_num, '(',
                      times_and_seqs[1], ')) is', hit_counter, 'out of',
                      (num_of_h_periods_to_check-1))

                pattern_num += 1
                stream.close()


def main():

    num_of_h_periods_to_verify = 50
    sched_dir = '../CAN_DATA/SAE/'
    json_dir = '../CAN_DATA/SAE/patterns_found/'
    scheds_and_info = '../CAN_DATA/SAE/schedule-specs-per-file.csv'
    optimization_method = 0

    for i in range(10):
        delete_json_files(json_dir)
        num_of_h_periods_to_analyze = i+1
        get_pattern_instance_info(num_of_h_periods_to_analyze,
                                  scheds_and_info, sched_dir, json_dir)

        print('\n========================================================')
        print('Starting accuracy analysis based on', i+1, 'hyperperiod(s).')
        print('========================================================\n')

        verify_target_times(num_of_h_periods_to_verify,
                            num_of_h_periods_to_analyze, json_dir, sched_dir,
                            optimization_method)



if __name__ == '__main__':
    main()
