import argparse
import json
import csv
from math import floor, inf

parser = argparse.ArgumentParser()
parser.add_argument("pos_diff_csv")
parser.add_argument("tle_times")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.tle_times, "r") as times_json:
    tle_times = json.load(times_json)

satnum = len(tle_times["sat_times"])

fit_period_len_limit = int(43205 * 4 / 8)

# get mod pos_diffs
output_dict = {}
before_max_diff = 0
before_max_modnames_list = []
after_max_diff = 0
after_max_modnames_list = []

sat_counter = 0
diff_csv_fname = args.pos_diff_csv.split("/")[-1]


with open(args.pos_diff_csv, "r") as diff_csv:
    row_reader = csv.reader(diff_csv)
    header = row_reader.__next__()

    for row in row_reader:
        mod_dict = {}
        modname = row[0]
        mod_diffs = [float(diff) for diff in row[1:]]
        epoch_sec = int(float(tle_times["sat_times"][modname]["offset_to_start"])) 

        before_avg_diff = None
        after_avg_diff = None

        mod_secs_after_epoch = 0
        mod_secs_before_epoch = 0

        if epoch_sec > 0:
            if epoch_sec < 43205:
                mod_secs_before_epoch = epoch_sec
            else:
                mod_secs_before_epoch = 43205
            mod_secs_after_epoch = 43205 - mod_secs_before_epoch
        else:
            mod_secs_before_epoch = 0
            mod_secs_after_epoch = 43205

        # backward max
        if mod_secs_before_epoch >= fit_period_len_limit and mod_secs_before_epoch < 43205:
            before_diffs = list(reversed(mod_diffs[:(mod_secs_before_epoch+1)]))[:fit_period_len_limit + 1]
            max_diff = max(before_diffs)
            if max_diff > before_max_diff:
                before_max_modnames_list.insert(0, modname)
                before_max_diff = max_diff


        # forward max
        if mod_secs_after_epoch >= fit_period_len_limit and mod_secs_after_epoch < 43205:
            
            diff_idx_offset = 0
            if epoch_sec >= 0:
                diff_idx_offset = epoch_sec
            else:
                diff_idx_offset = 0

            after_diffs = mod_diffs[diff_idx_offset:(diff_idx_offset + mod_secs_after_epoch+1)][:fit_period_len_limit + 1]
            max_diff = max(after_diffs)
            if max_diff > after_max_diff:
                after_max_diff = max_diff
                after_max_modnames_list.insert(0, modname)
        
        sat_counter += 1 
        print(f"{diff_csv_fname}: {sat_counter}/{satnum}")

output_dict["before_max_diff"] = before_max_diff
output_dict["before_max_modname"] = before_max_modnames_list
output_dict["after_max_diff"] = after_max_diff
output_dict["after_max_modnames"] = after_max_modnames_list

with open(args.output_path, "w") as out_f:
    json.dump(output_dict, out_f, indent=4)
