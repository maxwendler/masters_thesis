import argparse
import csv
import json

parser = argparse.ArgumentParser(prog="const_period_interval_differences",
                                 description="""Calculates differences between the (zenith) intervals of the communication periods
                                            of all satellite modules of a constellation between the reference mobility and alternative (new)
                                            mobility and outputs them to a JSON. The resulting statistics are: differences between the intervals of 
                                            periods existing for both mobilities; min, avg and max change/difference of such intervals; changes due to new
                                            and missing periods w.r.t. the reference mobility and their min, avg, max.
                                            """)

parser.add_argument("ref_periods_csv")
parser.add_argument("new_periods_csv")
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("output_path")
args = parser.parse_args()

ref_periods = {}
with open(args.ref_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        ref_periods[ f"{row[0]}{str(modname_to_id_num)}" ] = (int(row[1]), int(row[2]))
        modname_to_id_num += 1

new_periods = {}
with open(args.new_periods_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()
    modname_to_id_num = 0
    for row in row_reader:
        new_periods[ f"{row[0]}{str(modname_to_id_num)}" ] = (int(row[1]), int(row[2]))
        modname_to_id_num += 1

# keys returned in insertion order, i.e. order along sim. time is maintained
ref_period_names = list(ref_periods.keys())
new_period_names = list(new_periods.keys())

new_period_idx = 0
same_periods_interval_differences = {}
consecutive_missing_periods = []
current_consecutive_missing_periods = {
    "period_list": [],
    "prev_missing_new_end_sec": None,
    "after_missing_new_start_sec": None,
    "prev_missing_new_period": None,
    "after_missing_new_origin_period": None,
    "after_missing_new_origin_is_added_period": None
}
consecutive_added_periods = []
prev_ref_end_sec = 0
prev_ref_p_modname = "start"
prev_new_end_sec = 0

for ref_period_idx in range(len(ref_period_names)):

    new_periods_num_in_name_offset = ref_period_idx - new_period_idx

    # missing periods at the end of the ref list
    if new_period_idx >= len(new_periods):
        if len(current_consecutive_missing_periods["period_list"]) == 0:
            current_consecutive_missing_periods["prev_missing_new_end_sec"] = prev_new_end_sec
        current_consecutive_missing_periods["period_list"].append(ref_period_name)
        if ref_period_idx == len(ref_periods) - 1:
            current_consecutive_missing_periods["after_missing_new_start_sec"] = args.sim_time_limit
            current_consecutive_missing_periods["after_missing_new_origin_period"] = "end"
            current_consecutive_missing_periods["after_missing_new_origin_is_added_period"] = False
            consecutive_missing_periods.append(current_consecutive_missing_periods)
        continue        

    ref_period_name = ref_period_names[ref_period_idx]
    ref_period = ref_periods[ref_period_name]
    new_period_name = new_period_names[new_period_idx]
    new_period = new_periods[new_period_name]

    ref_interval = ref_period[0] - prev_ref_end_sec

    if ref_period_name == (new_period_name.split("]")[0] + "]" + str( int(new_period_name.split("]")[1]) + new_periods_num_in_name_offset )):
        # same interval -> simply calculate difference
        
        if len(current_consecutive_missing_periods["period_list"]) > 0:
            current_consecutive_missing_periods["after_missing_new_start_sec"] = new_period[0]
            current_consecutive_missing_periods["after_missing_new_origin_period"] = new_period_name
            current_consecutive_missing_periods["after_missing_new_origin_is_added_period"] = False
            consecutive_missing_periods.append(current_consecutive_missing_periods)
            current_consecutive_missing_periods = {
                "period_list": [],
                "prev_missing_new_end_sec": None,
                "after_missing_new_start_sec": None,
                "prev_missing_new_period": None,
                "after_missing_new_origin_period": None,
                "after_missing_new_origin_is_added_period": None
            }

        new_interval = new_period[0] - prev_new_end_sec
        prev_new_end_sec = new_period[1]

        same_periods_interval_differences[ f"{prev_ref_p_modname}-{ref_period_name}" ] = new_interval - ref_interval
        prev_ref_p_modname = ref_period_name
        prev_ref_end_sec = ref_period[1]
        new_period_idx += 1

    # mismatch because period is missing or a new period exists
    else:
        # comparison with a new period? -> try to find ref_period in remaining ones
        added_periods_num = 0
        related_new_period = None
        potentially_added_periods = {"period_list": [new_period_name],
                                     "prev_added_new_end_sec": prev_new_end_sec,
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
                related_new_period = new_periods[new_period_search_name]
                added_periods_num = new_period_search_idx - new_period_idx
                potentially_added_periods["after_added_new_start_sec"] = related_new_period[0]
                break
            # don't add period that matches again
            else:
                potentially_added_periods["period_list"].append(new_period_search_name)
            
        # comparison with new period confirmed -> calc interval difference to same period in new periods
        if added_periods_num > 0:
            
            if len(current_consecutive_missing_periods["period_list"]) > 0:
                current_consecutive_missing_periods["after_missing_new_start_sec"] = related_new_period[0]
                current_consecutive_missing_periods["after_missing_new_origin_period"] = new_period_search_name
                current_consecutive_missing_periods["after_missing_new_origin_is_added_period"] = True
                consecutive_missing_periods.append(current_consecutive_missing_periods)
                current_consecutive_missing_periods = {
                    "period_list": [],
                    "prev_missing_new_end_sec": None,
                    "after_missing_new_start_sec": None,
                    "prev_missing_new_period": None,
                    "after_missing_new_origin_period": None,
                    "after_missing_new_origin_is_added_period": None
                }

            # actual added periods
            consecutive_added_periods.append(potentially_added_periods)

            new_interval = related_new_period[0] - prev_new_end_sec
            prev_new_end_sec = related_new_period[1]

            same_periods_interval_differences[f"{prev_ref_p_modname}-{ref_period_name}"] = new_interval - ref_interval            

            new_period_idx += added_periods_num + 1
            prev_ref_p_modname = ref_period_name
            prev_ref_end_sec = ref_period[1]

        # comparison with new period not confirmed -> lost period -> skip ref_period
        else:
            if len(current_consecutive_missing_periods["period_list"]) == 0:
                current_consecutive_missing_periods["prev_missing_new_end_sec"] = prev_new_end_sec
                current_consecutive_missing_periods["prev_missing_new_period"] = prev_ref_p_modname
            current_consecutive_missing_periods["period_list"].append(ref_period_name)

# added period at end of new lsit
if new_period_idx < len(new_periods):
    period_list = []
    for i in range(new_period_idx, len(new_periods)):
        period_list.append(new_period_names[i])

    consecutive_added_periods.append({"period_list": period_list,
        "prev_added_new_end_sec": prev_new_end_sec,
        "prev_added_period_name": prev_ref_p_modname,
        "after_added_period_name": "end",
        "after_added_new_start_sec": args.sim_time_limit,
        "original_interval": args.sim_time_limit - prev_ref_end_sec
        }
    )

# get data for missing periods
consecutive_missing_periods_changes = {}
if len(consecutive_missing_periods) > 0:
    
    ref_period_idx = 0
    
    for current_consecutive_missing_periods in consecutive_missing_periods:
        
        prev_end_sec = 0
        intervals_including_missing = []
        current_consecutive_missing_periods_period_list = current_consecutive_missing_periods["period_list"]

        for ref_period_subidx in range(ref_period_idx, len(ref_period_names)):
            
            # periods missing from start -> no search necessary
            if ref_period_idx == 0:

                prev_end_sec = 0

                for iterate_over_current_missing_idx in range(ref_period_subidx + 1, ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)):
                    
                    current_period = ref_periods[ref_period_names[iterate_over_current_missing_idx]]
                    intervals_including_missing.append(current_period[0] - prev_end_sec)
                    prev_end_sec = current_period[1]

                after_missing_ref_period_start_sec = ref_periods[ref_period_names[ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)]][0]
                intervals_including_missing.append(after_missing_ref_period_start_sec - prev_end_sec)
                ref_period_idx = ref_period_subidx + 2
                break
            
            # search for missing periods to get their data
            else:
                if ref_period_names[ref_period_subidx + 1] == current_consecutive_missing_periods_period_list[0]:
                    
                    prev_end_sec = ref_periods[ref_period_names[ref_period_subidx]][1]
                    
                    for iterate_over_current_missing_idx in range(ref_period_subidx + 1, ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)):
                        
                        current_period = ref_periods[ref_period_names[iterate_over_current_missing_idx]]
                        intervals_including_missing.append(current_period[0] - prev_end_sec)
                        prev_end_sec = current_period[1]

                    after_missing_ref_period_start_sec = ref_periods[ref_period_names[ref_period_subidx + 1 + len(current_consecutive_missing_periods_period_list)]][0]
                    intervals_including_missing.append(after_missing_ref_period_start_sec - prev_end_sec)
                    ref_period_idx = ref_period_subidx + 2
                    break

        consecutive_missing_periods_changes[f"{current_consecutive_missing_periods_period_list[0]}_to_{current_consecutive_missing_periods_period_list[-1]}"] = {
            "original_intervals": intervals_including_missing,
            "new_interval": current_consecutive_missing_periods["after_missing_new_start_sec"] - current_consecutive_missing_periods["prev_missing_new_end_sec"],
            "new_interval_start_period": current_consecutive_missing_periods["prev_missing_new_period"],
            "new_interval_end_period": current_consecutive_missing_periods["after_missing_new_origin_period"],
            "new_interval_end_period_is_added_period": current_consecutive_missing_periods["after_missing_new_origin_is_added_period"]
        }

# get data for added periods
consecutive_added_periods_changes = {}
for current_consecutive_added_periods in consecutive_added_periods:

    prev_end_sec = current_consecutive_added_periods["prev_added_new_end_sec"]
    new_intervals = []
    for added_period_name in current_consecutive_added_periods["period_list"]:
        added_period = new_periods[added_period_name]
        new_intervals.append(added_period[0] - prev_end_sec)
        prev_end_sec = added_period[1]
    new_intervals.append(current_consecutive_added_periods["after_added_new_start_sec"] - prev_end_sec)

    consecutive_added_periods_changes[f"between {current_consecutive_added_periods['prev_added_period_name']} and {current_consecutive_added_periods['after_added_period_name']}"] = {
        "original_interval": current_consecutive_added_periods['original_interval'],
        "added_periods": current_consecutive_added_periods["period_list"],
        "new_intervals": new_intervals
    }

output = {
    "same_periods_changes": same_periods_interval_differences,
    "consecutive_missing_periods_changes": consecutive_missing_periods_changes,
    "consecutive_added_periods_changes": consecutive_added_periods_changes
}

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)