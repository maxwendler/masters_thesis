import argparse
import csv
import json
import os

parser = argparse.ArgumentParser(prog="const_period_zenith_interval_differences",
                                 description="""Calculates differences between the zenith intervals of the communication periods
                                            of all satellite modules of a constellation between the reference mobility and alternative (new)
                                            mobility and outputs them to a JSON. The resulting statistics are: differences between the intervals of 
                                            periods existing for both mobilities; min, avg and max change/difference of such intervals; changes due to new
                                            and missing periods w.r.t. the reference mobility and their min, avg, max.
                                            """)
parser.add_argument("ref_periods_csv")
parser.add_argument("ref_periods_jsons_dir")
parser.add_argument("new_periods_csv")
parser.add_argument("new_periods_jsons_dir")
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("output_path")
args = parser.parse_args()

ref_periods_jsons_dir = args.ref_periods_jsons_dir if args.ref_periods_jsons_dir.endswith("/") else args.ref_periods_jsons_dir + "/"
new_periods_jsons_dir = args.new_periods_jsons_dir if args.new_periods_jsons_dir.endswith("/") else args.new_periods_jsons_dir + "/"

ref_period_names = []
with open(args.ref_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        ref_period_names.append( f"{row[0]}{str(modname_to_id_num)}" ) 
        modname_to_id_num += 1

ref_periods_zeniths = {}
for period_json_fname in filter(lambda fname: fname.endswith("communication-periods.json"), os.listdir(ref_periods_jsons_dir)):

    with open(ref_periods_jsons_dir + period_json_fname, "r") as json_f:
        comm_periods = json.load(json_f)
    
    modname = comm_periods['modname']
    modname_period_names = list(filter(lambda pname: pname.startswith(modname), ref_period_names))

    for zenith_idx in range(len(modname_period_names)):
        zenith = comm_periods["zenith_times"][zenith_idx]
        period_name = modname_period_names[zenith_idx]
        ref_periods_zeniths[period_name] = zenith

new_period_names = []
with open(args.new_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        new_period_names.append( f"{row[0]}{str(modname_to_id_num)}" ) 
        modname_to_id_num += 1

new_periods_zeniths = {}
for period_json_fname in filter(lambda fname: fname.endswith("communication-periods.json"), os.listdir(new_periods_jsons_dir)):

    with open(new_periods_jsons_dir + period_json_fname, "r") as json_f:
        comm_periods = json.load(json_f)
    
    modname = comm_periods['modname']
    modname_period_names = list(filter(lambda pname: pname.startswith(modname), new_period_names))

    for zenith_idx in range(len(modname_period_names)):
        zenith = comm_periods["zenith_times"][zenith_idx]
        period_name = modname_period_names[zenith_idx]
        new_periods_zeniths[period_name] = zenith

new_period_idx = 0
same_periods_interval_differences = {}
consecutive_missing_periods = []
current_consecutive_missing_periods = {
    "period_list": [],
    "prev_missing_new_zenith": None,
    "after_missing_new_zenith": None,
    "prev_missing_ref_period": None,
    "after_missing_period": None,
    "after_missing_period_is_added_and_new": None
}
consecutive_added_periods = []
prev_ref_zenith = 0
prev_ref_p_modname = "start"
prev_new_zenith = 0

for ref_period_idx in range(len(ref_period_names)):

    new_periods_num_in_name_offset = ref_period_idx - new_period_idx

    # missing periods at the end of the ref list
    if new_period_idx >= len(new_period_names):
        if len(current_consecutive_missing_periods["period_list"]) == 0:
            current_consecutive_missing_periods["prev_missing_new_zenith"] = prev_new_zenith
            current_consecutive_missing_periods["prev_missing_ref_period"] = prev_ref_p_modname
        current_consecutive_missing_periods["period_list"].append(ref_period_name)
        if ref_period_idx == len(ref_period_names) - 1:
            current_consecutive_missing_periods["after_missing_new_zenith"] = args.sim_time_limit
            current_consecutive_missing_periods["after_missing_period"] = "end"
            current_consecutive_missing_periods["after_missing_period_is_added_and_new"] = False
            consecutive_missing_periods.append(current_consecutive_missing_periods)
        continue        

    ref_period_name = ref_period_names[ref_period_idx]
    ref_period_zenith = ref_periods_zeniths[ref_period_name]
    new_period_name = new_period_names[new_period_idx]
    new_period_zenith = new_periods_zeniths[new_period_name]

    ref_interval = ref_period_zenith - prev_ref_zenith

    if ref_period_name == (new_period_name.split("]")[0] + "]" + str( int(new_period_name.split("]")[1]) + new_periods_num_in_name_offset )):
        # same interval -> simply calculate difference
        
        if len(current_consecutive_missing_periods["period_list"]) > 0:
            current_consecutive_missing_periods["after_missing_new_zenith"] = new_period_zenith
            current_consecutive_missing_periods["after_missing_period"] = ref_period_name
            current_consecutive_missing_periods["after_missing_period_is_added_and_new"] = False
            consecutive_missing_periods.append(current_consecutive_missing_periods)
            current_consecutive_missing_periods = {
                "period_list": [],
                "prev_missing_new_zenith": None,
                "after_missing_new_zenith": None,
                "prev_missing_ref_period": None,
                "after_missing_period": None,
                "after_missing_period_is_added_and_new": None
            }

        new_interval = new_period_zenith - prev_new_zenith
        prev_new_zenith = new_period_zenith

        same_periods_interval_differences[ f"{prev_ref_p_modname}-{ref_period_name}" ] = new_interval - ref_interval
        prev_ref_p_modname = ref_period_name
        prev_ref_zenith = ref_period_zenith
        new_period_idx += 1

    # mismatch because period is missing or a new period exists
    else:
        # comparison with a new period? -> try to find ref_period in remaining ones
        added_periods_num = 0
        related_new_period_zenith = None
        potentially_added_periods = {"period_list": [new_period_name],
                                     "prev_added_new_zenith": prev_new_zenith,
                                     "prev_added_period_name": prev_ref_p_modname,
                                     "after_added_period_name": ref_period_name,
                                     "original_interval": ref_interval}
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
                potentially_added_periods["after_added_new_zenith"] = related_new_period_zenith
                break
            # don't add period that matches again
            else:
                potentially_added_periods["period_list"].append(new_period_search_name)
            
        # comparison with new period confirmed -> calc interval difference to same period in new periods
        if added_periods_num > 0:
            
            if len(current_consecutive_missing_periods["period_list"]) > 0:
                current_consecutive_missing_periods["after_missing_new_zenith"] = related_new_period_zenith
                current_consecutive_missing_periods["after_missing_period"] = new_period_search_name
                current_consecutive_missing_periods["after_missing_period_is_added_and_new"] = True
                consecutive_missing_periods.append(current_consecutive_missing_periods)
                current_consecutive_missing_periods = {
                    "period_list": [],
                    "prev_missing_new_zenith": None,
                    "after_missing_new_zenith": None,
                    "prev_missing_ref_period": None,
                    "after_missing_period": None,
                    "after_missing_period_is_added_and_new": None
                }

            # actual added periods
            consecutive_added_periods.append(potentially_added_periods)

            new_interval = related_new_period_zenith - prev_new_zenith
            prev_new_zenith = related_new_period_zenith

            same_periods_interval_differences[f"{prev_ref_p_modname}-{ref_period_name}"] = new_interval - ref_interval            

            new_period_idx += added_periods_num + 1
            prev_ref_p_modname = ref_period_name
            prev_ref_zenith = ref_period_zenith

        # comparison with new period not confirmed -> lost period -> skip ref_period
        else:
            if len(current_consecutive_missing_periods["period_list"]) == 0:
                current_consecutive_missing_periods["prev_missing_new_zenith"] = prev_new_zenith
                current_consecutive_missing_periods["prev_missing_ref_period"] = prev_ref_p_modname
            current_consecutive_missing_periods["period_list"].append(ref_period_name)

# added period at end of new list
if new_period_idx < len(new_periods_zeniths):
    period_list = []
    for i in range(new_period_idx, len(new_periods_zeniths)):
        period_list.append(new_period_names[i])

    consecutive_added_periods.append({"period_list": period_list,
        "prev_added_new_zenith": prev_new_zenith,
        "prev_added_period_name": prev_ref_p_modname,
        "after_added_period_name": "end",
        "after_added_new_zenith": args.sim_time_limit,
        "original_interval": args.sim_time_limit - prev_ref_zenith
        }
    )

# get data for missing periods
consecutive_missing_periods_changes = {}
if len(consecutive_missing_periods) > 0:
    
    ref_period_idx = 0
    
    for current_consecutive_missing_periods in consecutive_missing_periods:
        
        prev_end_zenith = 0
        intervals_including_missing = []
        current_consecutive_missing_periods_period_list = current_consecutive_missing_periods["period_list"]

        # periods missing from start -> no search necessary
        if current_consecutive_missing_periods_period_list[0] == ref_period_names[0]:

            prev_end_zenith = 0

            for iterate_over_current_missing_idx in range(ref_period_subidx + 1, ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)):
                
                current_zenith = ref_periods_zeniths[ref_period_names[iterate_over_current_missing_idx]]
                intervals_including_missing.append(current_zenith - prev_end_zenith)
                prev_end_zenith = current_zenith

            after_missing_ref_period_zenith = ref_periods_zeniths[ref_period_names[ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)]][0]
            intervals_including_missing.append(after_missing_ref_period_zenith - prev_end_zenith)
            ref_period_idx = ref_period_subidx + 2

        # search for missing periods to get their data
        else:
            for ref_period_subidx in range(ref_period_idx, len(ref_period_names)):
                if ref_period_names[ref_period_subidx + 1] == current_consecutive_missing_periods_period_list[0]:
                    
                    prev_end_zenith = ref_periods_zeniths[ref_period_names[ref_period_subidx]]
                    
                    for iterate_over_current_missing_idx in range(ref_period_subidx + 1, ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)):
                        
                        current_zenith = ref_periods_zeniths[ref_period_names[iterate_over_current_missing_idx]]
                        intervals_including_missing.append(current_zenith - prev_end_zenith)
                        prev_end_zenith = current_zenith

                    after_missing_ref_period_zenith = ref_periods_zeniths[ref_period_names[ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)]]
                    intervals_including_missing.append(after_missing_ref_period_zenith - prev_end_zenith)
                    ref_period_idx = ref_period_subidx + 2
                    break
        
        new_interval = current_consecutive_missing_periods["after_missing_new_zenith"] - current_consecutive_missing_periods["prev_missing_new_zenith"]
        
        interval_changes = []
        for interval in intervals_including_missing:
            interval_changes.append(new_interval - interval)
        avg_interval_change = sum(interval_changes) / len(interval_changes)

        consecutive_missing_periods_changes[f"{current_consecutive_missing_periods_period_list[0]}_to_{current_consecutive_missing_periods_period_list[-1]}"] = {
            "original_intervals": intervals_including_missing,
            "new_interval": new_interval,
            "interval_changes": interval_changes,
            "avg_interval_change": avg_interval_change,
            "new_interval_start_period": current_consecutive_missing_periods["prev_missing_ref_period"],
            "new_interval_end_period": current_consecutive_missing_periods["after_missing_period"],
            "new_interval_end_period_is_added_period": current_consecutive_missing_periods["after_missing_period_is_added_and_new"]
        }

# get data for added periods
consecutive_added_periods_changes = {}
for current_consecutive_added_periods in consecutive_added_periods:

    prev_end_zenith = current_consecutive_added_periods["prev_added_new_zenith"]
    new_intervals = []
    for added_period_name in current_consecutive_added_periods["period_list"]:
        added_period_zenith = new_periods_zeniths[added_period_name]
        new_intervals.append(added_period_zenith - prev_end_zenith)
        prev_end_zenith = added_period_zenith
    new_intervals.append(current_consecutive_added_periods["after_added_new_zenith"] - prev_end_zenith)

    interval_changes = []
    for interval in new_intervals:
        interval_changes.append(interval - current_consecutive_added_periods['original_interval'])
    avg_interval_change = sum(interval_changes) / len(interval_changes)

    consecutive_added_periods_changes[f"between {current_consecutive_added_periods['prev_added_period_name']} and {current_consecutive_added_periods['after_added_period_name']}"] = {
        "original_interval": current_consecutive_added_periods['original_interval'],
        "added_periods": current_consecutive_added_periods["period_list"],
        "new_intervals": new_intervals,
        "interval_changes": interval_changes,
        "avg_interval_change": avg_interval_change
    }

output = {
    "same_periods_changes": same_periods_interval_differences,
    "consecutive_missing_periods_changes": consecutive_missing_periods_changes,
    "consecutive_added_periods_changes": consecutive_added_periods_changes
}

min_same_interval_diff = min(same_periods_interval_differences.values())
max_same_interval_diff = max(same_periods_interval_differences.values())
avg_same_interval_diff = sum(same_periods_interval_differences.values()) / len(same_periods_interval_differences)

missing_interval_changes = []
for consecutive_missing_periods_change in consecutive_missing_periods_changes.values():
    missing_interval_changes.append(consecutive_missing_periods_change["avg_interval_change"])
if len(missing_interval_changes) > 0:
    avg_missing_interval_change = sum(missing_interval_changes) / len(missing_interval_changes)
else:
    avg_missing_interval_change = None

added_interval_changes = []
for consecutive_added_periods_change in consecutive_added_periods_changes.values():
    added_interval_changes.append(consecutive_added_periods_change["avg_interval_change"])
if len(added_interval_changes) > 0:
    avg_added_interval_change = sum(added_interval_changes) / len(added_interval_changes)
else:
    avg_added_interval_change = None

summary = {"min_same_interval_diff": min_same_interval_diff,
           "max_same_interval_diff": max_same_interval_diff,
           "avg_same_interval_diff": avg_same_interval_diff,
           "avg_missing_interval_change": avg_missing_interval_change,
           "avg_added_interval_change": avg_added_interval_change}

output["summary"] = summary

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)