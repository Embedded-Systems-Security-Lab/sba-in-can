from schedule_attack.utils.process_file import *
from schedule_attack.reverse_engineer.reverse_log import ReverseLogs
from schedule_attack.utils.general import *



def get_hyperperiod_list(data,hyperperiod=None):
  hyperperiod_list = []
  for msg in data:
    if hyperperiod != None:
      if msg.timestamp > hyperperiod:
        return hyperperiod_list
    hyperperiod_list.append(msg.id)
  return hyperperiod_list

def get_preceded_id(sequence_list):
    res = {}
    for i in range(1, len(sequence_list)):
        id = sequence_list[i]
        if id in res:
            if sequence_list[i-1] not in res[id]:
                res[id].append(sequence_list[i-1])
        else:
            res[id] = [sequence_list[i-1]]

    return res



file_path = './OAK-old/Attack_free_dataset.csv'
bus_speed = 500000
r = ReverseLogs(file_path, bus_speed) #Using bus_speed of 500kbs
r_info = r.period_bounds()
data = ProcessFile.process_oak_old_data(file_path, bus_speed)
keys = [key for key in r_info if key != 1]
periods = [r_info[key] for key in keys if key != 1]

hyperperiod = General.lcm(periods)
print(hyperperiod) # Round off error from floating number
# Using manual inspection
hyperperiod = 1.009745
#hyperperiod = 1
sequence = 1 * hyperperiod

sequence_list = get_hyperperiod_list(data, sequence)

result = get_preceded_id(sequence_list)

num_res = {}

for key in result:
    count = len(result[key])
    if count in num_res:
        num_res[count] += 1
    else:
        num_res[count] = 1

print(num_res)
