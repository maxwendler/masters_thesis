import argparse
import csv

parser = argparse.ArgumentParser(prog="const_period_interval_differences",
                                 description="""Calculates differences between the (zenith) intervals of the communication periods
                                            of all satellite modules of a constellation between the reference mobility and alternative (new)
                                            mobility and outputs them to a JSON. The resulting statistics are: differences between the intervals of 
                                            periods existing for both mobilities; min, avg and max change/difference of such intervals; changes due to new
                                            and missing periods w.r.t. the reference mobility and their min, avg, max.
                                            """)

parser.add_argument("ref_periods_csv")
parser.add_argument("new_periods_csv")
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
    "after_missing_new_origin_period": None,
    "after_missing_new_origin_is_added_period": None
}
prev_ref_end_sec = 0
prev_ref_p_modname = "start"
prev_new_end_sec = 0

for ref_period_idx in range(len(ref_period_names)):
    
    new_periods_num_in_name_offset = ref_period_idx - new_period_idx

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
                "after_missing_new_origin_period": None,
                "after_missing_new_origin_is_added_period": None
            }

        new_interval = new_period[0] - prev_new_end_sec
        prev_new_end_sec = new_period[1]

        same_periods_interval_differences[( prev_ref_p_modname, ref_period_name )] = new_interval - ref_interval
        prev_ref_p_modname = ref_period_name
        prev_ref_end_sec = ref_period[1]
        new_period_idx += 1

    # mismatch because period is missing or a new period exists
    else:
        # comparison with a new period? -> try to find ref_period in remaining ones
        added_periods_num = 0
        related_new_period = None
        for new_period_search_idx in range(new_period_idx + 1, len(new_period_names)):
            
            new_period_search_name = new_period_names[new_period_search_idx]
            if (new_period_search_name.split("]")[0] + "]" + str(new_period_search_idx - 1 + new_periods_num_in_name_offset) ) == ref_period_name:
                related_new_period = new_periods[new_period_search_name]
                added_periods_num = new_period_search_idx - new_period_idx
                break
            
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
                    "after_missing_new_origin_period": None,
                    "after_missing_new_origin_is_added_period": None
                }

            new_interval = related_new_period[0] - prev_new_end_sec
            prev_new_end_sec = related_new_period[1]

            same_periods_interval_differences[prev_ref_p_modname, ref_period_name] = new_interval - ref_interval            

            new_period_idx += added_periods_num + 1
            prev_ref_p_modname = ref_period_name
            prev_ref_end_sec = ref_period[1]

        # comparison with new period not confirmed -> lost period -> skip ref_period
        else:
            if len(current_consecutive_missing_periods["period_list"]) == 0:
                current_consecutive_missing_periods["prev_missing_new_end_sec"] = prev_new_end_sec
            current_consecutive_missing_periods["period_list"].append(ref_period_name)
            pass

# get data for missing periods
consecutive_missing_periods_changes = {}
if len(consecutive_missing_periods) > 0:
    
    ref_period_idx = 0
    
    for current_consecutive_missing_periods in consecutive_missing_periods:
        
        prev_end_sec = 0
        intervals_including_missing = []
        current_consecutive_missing_periods_period_list = current_consecutive_missing_periods["period_list"]

        for ref_period_subidx in range(ref_period_idx, len(ref_period_names)):
            
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
            "new_interval_end_period": current_consecutive_missing_periods["after_missing_new_origin_period"],
            "new_interval_end_period_is_added_period": current_consecutive_missing_periods["after_missing_new_origin_is_added_period"]
        }

print("hurray")