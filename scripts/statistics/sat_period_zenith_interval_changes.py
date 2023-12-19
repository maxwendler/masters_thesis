import argparse
import csv
import json
import os

parser = argparse.ArgumentParser(prog="sat_period_zenith_interval_differences")
parser.add_argument("modname")
parser.add_argument("ref_periods_csv")
parser.add_argument("ref_periods_json")
parser.add_argument("new_periods_csv")
parser.add_argument("new_periods_json")
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("output_path")
args = parser.parse_args()

ref_period_names = []
with open(args.ref_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        modname = row[0]
        if modname == args.modname:
            ref_period_names.append( f"{row[0]}{str(modname_to_id_num)}" ) 
            modname_to_id_num += 1

ref_periods_zeniths = {}
ref_periods_offsets = {}
with open(args.ref_periods_json, "r") as json_f:
    comm_periods = json.load(json_f)

for zenith_idx in range(len(ref_period_names)):
    zenith = comm_periods["zenith_times"][zenith_idx]
    offset_to_epoch = comm_periods["period_start_to_epoch_offsets"][zenith_idx]
    period_name = ref_period_names[zenith_idx]
    ref_periods_zeniths[period_name] = zenith
    ref_periods_offsets[period_name] = offset_to_epoch

new_period_names = []
with open(args.new_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        modname = row[0]
        if modname == args.modname:
            new_period_names.append( f"{row[0]}{str(modname_to_id_num)}" ) 
            modname_to_id_num += 1

new_periods_zeniths = {}
with open(args.new_periods_json, "r") as json_f:
    comm_periods = json.load(json_f)

for zenith_idx in range(len(new_period_names)):
    zenith = comm_periods["zenith_times"][zenith_idx]
    period_name = new_period_names[zenith_idx]
    new_periods_zeniths[period_name] = zenith

new_period_idx = 0
same_periods_interval_changes = {}
prev_ref_zenith = 0
prev_ref_period_name = "start"
prev_new_zenith = 0

for ref_period_idx in range(len(ref_period_names)):

    new_periods_num_in_name_offset = ref_period_idx - new_period_idx

    # missing periods at the end of the ref list -> ignore
    if new_period_idx >= len(new_period_names):
        break

    ref_period_name = ref_period_names[ref_period_idx]
    ref_period_zenith = ref_periods_zeniths[ref_period_name]
    new_period_name = new_period_names[new_period_idx]
    new_period_zenith = new_periods_zeniths[new_period_name]

    ref_interval = ref_period_zenith - prev_ref_zenith
    
    abs_ref_offsets_sum	= None
    abs_offset_ref_dif = None
    start_offset = 0 if prev_ref_period_name == "start" else ref_periods_offsets[prev_ref_period_name]
    end_offset = ref_periods_offsets[ref_period_name]
    if prev_ref_period_name == "start":
        abs_ref_offsets_sum = abs(end_offset)
        abs_offset_ref_dif = 0
    else:
        abs_ref_offsets_sum = abs(end_offset) + abs(start_offset)
        abs_offset_ref_dif = abs(abs(end_offset) - abs(start_offset))

    if ref_period_name == (new_period_name.split("]")[0] + "]" + str( int(new_period_name.split("]")[1]) + new_periods_num_in_name_offset )):
        # same interval -> simply calculate difference

        new_interval = new_period_zenith - prev_new_zenith
        prev_new_zenith = new_period_zenith

        same_periods_interval_changes[f"{prev_ref_period_name}-{ref_period_name}"] = {
            "difference": new_interval - ref_interval,
            "start_offset": start_offset,
            "end_offset": end_offset,
            "abs_offset_sum": abs_ref_offsets_sum,
            "abs_offset_diff": abs_offset_ref_dif
        }

        prev_ref_period_name = ref_period_name
        prev_ref_zenith = ref_period_zenith
        new_period_idx += 1

    # mismatch because period is missing or a new period exists
    else:
        # comparison with a new period? -> try to find ref_period in remaining ones
        added_periods_num = 0
        related_new_period_zenith = None
        for new_period_search_idx in range(new_period_idx + 1, len(new_period_names)):
            
            new_period_search_name = new_period_names[new_period_search_idx]
            match_condition = None
            if ref_period_idx == 0:
                match_condition = new_period_search_name.split("]")[0] + "]" + str(new_period_search_idx - (new_period_search_idx - new_period_idx) + new_periods_num_in_name_offset)  == ref_period_name
            else:
                match_condition = new_period_search_name.split("]")[0] + "]" + str(new_period_search_idx - 1 + new_periods_num_in_name_offset)  == ref_period_name

            if match_condition:
                related_new_period_zenith = new_periods_zeniths[new_period_search_name]
                added_periods_num = new_period_search_idx - new_period_idx
                break
            
        # comparison with new period confirmed -> calc interval difference to same period in new periods
        if added_periods_num > 0:
            
            new_interval = related_new_period_zenith - prev_new_zenith
            prev_new_zenith = related_new_period_zenith

            same_periods_interval_changes[f"{prev_ref_period_name}-{ref_period_name}"] = {
                "difference": new_interval - ref_interval,
                "start_offset": start_offset,
                "end_offset": end_offset,
                "abs_offset_sum": abs_ref_offsets_sum,
                "abs_offset_diff": abs_offset_ref_dif
            }            

            new_period_idx += added_periods_num + 1
            prev_ref_period_name = ref_period_name
            prev_ref_zenith = ref_period_zenith

        # comparison with new period not confirmed -> lost period -> skip ref_period
        else:
            continue

# ignore added period at end of new list
# -> no code in comparison to constellation script

output = {
    "same_periods_changes": same_periods_interval_changes,
}

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)