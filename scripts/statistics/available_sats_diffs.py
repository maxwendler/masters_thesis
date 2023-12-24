import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("ref_mobility_availables_json")
parser.add_argument("new_mobility_availables_json")
parser.add_argument("all_interval_changes_json")
parser.add_argument("ref_comm_periods_dir")
parser.add_argument("new_comm_periods_dir")
parser.add_argument("output_path")
args = parser.parse_args()

ref_comm_periods_dir = args.ref_comm_periods_dir if args.ref_comm_periods_dir.endswith("/") else args.ref_comm_periods_dir + "/"
new_comm_periods_dir = args.new_comm_periods_dir if args.new_comm_periods_dir.endswith("/") else args.new_comm_periods_dir + "/"

with open(args.ref_mobility_availables_json, "r") as json_f:
    ref_availability_stats = json.load(json_f)

with open(args.new_mobility_availables_json, "r") as json_f:
    new_availability_stats = json.load(json_f)

with open(args.all_interval_changes_json, "r") as json_f:
    all_interval_changes = json.load(json_f)

measurement_start_time = ref_availability_stats["available_sats"][0]["sim_time"]

available_sat_diffs = []
abs_diff_sum = 0
times_with_num_diff = 0
for sim_time_idx in range(len(ref_availability_stats["available_sats"])):
    sim_time = measurement_start_time + sim_time_idx
    
    ref_current_available = ref_availability_stats["available_sats"][sim_time_idx]
    new_current_availabe = new_availability_stats["available_sats"][sim_time_idx]

    ref_sorted_sats = sorted(ref_current_available["sats"])
    new_sorted_sats = sorted(new_current_availabe["sats"])

    if ref_sorted_sats != new_sorted_sats:
        missing_sats = []
        for sat in ref_sorted_sats:
            if sat not in new_sorted_sats:
                missing_sats.append(sat)
        
        added_sats = []
        for sat in new_sorted_sats:
            if sat not in ref_sorted_sats:
                added_sats.append(sat)
        
        sat_num_diff = len(new_sorted_sats) - len(ref_sorted_sats)
        if sat_num_diff != 0:
            times_with_num_diff += 1
        abs_diff_sum += abs(sat_num_diff)

        available_sat_diffs.append({
            "sim_time": sim_time,
            "sat_num_diff": sat_num_diff,
            "missing_sats": missing_sats,
            "added_sats": added_sats  
        })

    else:
        available_sat_diffs.append({
            "sim_time": sim_time,
            "sat_num_diff": 0,
            "missing_sats": [],
            "added_sats": []
        })

availability_num_time_diffs = {}
for availability_num in ref_availability_stats["availability_num_times"].keys():
    ref_availability_num_time = ref_availability_stats["availability_num_times"][availability_num]
    new_availability_num_time = new_availability_stats["availability_num_times"][availability_num] if availability_num in new_availability_stats["availability_num_times"].keys() else 0
    availability_num_time_diffs[availability_num] = new_availability_num_time - ref_availability_num_time

for availability_num in new_availability_stats["availability_num_times"].keys():
    if availability_num not in availability_num_time_diffs.keys():
        availability_num_time_diffs[availability_num] = new_availability_stats["availability_num_times"][availability_num]

availability_num_ratio_diffs = {}
for availability_num in ref_availability_stats["availability_num_ratios"].keys():
    ref_availability_num_ratio = ref_availability_stats["availability_num_ratios"][availability_num]
    new_availability_num_ratio = new_availability_stats["availability_num_ratios"][availability_num] if availability_num in new_availability_stats["availability_num_ratios"].keys() else 0
    availability_num_ratio_diffs[availability_num] = new_availability_num_ratio - ref_availability_num_ratio

for availability_num in new_availability_stats["availability_num_ratios"].keys():
    if availability_num not in availability_num_ratio_diffs.keys():
        availability_num_ratio_diffs[availability_num] = new_availability_stats["availability_num_ratios"][availability_num]

# lost period effects
lost_period_effects = []
lost_periods_total_time = 0
lost_periods_total_availability_reductions_by_one = {}
for current_consecutive_lost_periods in all_interval_changes["consecutive_lost_periods"]:
    for period in current_consecutive_lost_periods:
        
        modname = period["period_name"].split("]")[0] + "]"

        with open(ref_comm_periods_dir +  modname + "_communication-periods.json", "r") as json_f:
            mod_comm_periods = json.load(json_f)

        period_times = mod_comm_periods["periods"][period["sat_period_idx"]]
        period_duration = mod_comm_periods["durations"][period["sat_period_idx"]]
        lost_periods_total_time += period_duration

        availability_reductions_by_one = {}
        for sim_time in range(period_times[0], period_times[1]):
            original_availability = ref_availability_stats["available_sats"][sim_time - measurement_start_time]["sat_num"]
            availability_reduction_key = f"{original_availability}->{original_availability - 1}"
            if availability_reduction_key in availability_reductions_by_one.keys():
                availability_reductions_by_one[availability_reduction_key] += 1
            else:
                availability_reductions_by_one[availability_reduction_key] = 1

        for availability_reduction_key in availability_reductions_by_one.keys():
            if availability_reduction_key in lost_periods_total_availability_reductions_by_one.keys():
                lost_periods_total_availability_reductions_by_one[availability_reduction_key] += availability_reductions_by_one[availability_reduction_key]
            else:
                lost_periods_total_availability_reductions_by_one[availability_reduction_key] = availability_reductions_by_one[availability_reduction_key]

        lost_period_effects.append({
            "sat": modname,
            "sat_period_idx": period["sat_period_idx"],
            "period_seq_num": period["period_name"].split("]")[1],
            "period": period_times,
            "duration": period_duration,
            "availability_reductions_by_one": availability_reductions_by_one
        })

# added periods effects
added_period_effects = []
added_periods_total_time = 0
added_periods_total_availability_increases_by_one = {}
for current_consecutive_added_periods in all_interval_changes["consecutive_added_periods"]:
    for period in current_consecutive_added_periods:
        
        modname = period["period_name"].split("]")[0] + "]"

        with open(new_comm_periods_dir +  modname + "_communication-periods.json", "r") as json_f:
            mod_comm_periods = json.load(json_f)

        period_times = mod_comm_periods["periods"][period["sat_period_idx"]]
        period_duration = mod_comm_periods["durations"][period["sat_period_idx"]]
        added_periods_total_time += period_duration

        availability_increases_by_one = {}
        for sim_time in range(period_times[0], period_times[1]):
            original_availability = ref_availability_stats["available_sats"][sim_time - measurement_start_time]["sat_num"]
            availability_increase_key = f"{original_availability}->{original_availability + 1}"
            if availability_increase_key in availability_increases_by_one.keys():
                availability_increases_by_one[availability_increase_key] += 1
            else:
                availability_increases_by_one[availability_increase_key] = 1

        for availability_increase_key in availability_increases_by_one.keys():
            if availability_increase_key in added_periods_total_availability_increases_by_one.keys():
                added_periods_total_availability_increases_by_one[availability_increase_key] += availability_increases_by_one[availability_increase_key]
            else:
                added_periods_total_availability_increases_by_one[availability_increase_key] = availability_increases_by_one[availability_increase_key]

        added_period_effects.append({
            "sat": modname,
            "sat_period_idx": period["sat_period_idx"],
            "period_seq_num": period["period_name"].split("]")[1],
            "period": period_times,
            "duration": period_duration,
            "availability_increases_by_one": availability_increases_by_one
        })

output = {
    "avg_abs_sat_num_diff": abs_diff_sum / len(available_sat_diffs),
    "time_with_num_diff_to_total_time": times_with_num_diff / len(available_sat_diffs),
    "availability_num_time_diffs": availability_num_time_diffs,
    "availability_num_ratio_diffs": availability_num_ratio_diffs,
    "lost_periods_effects": {
        "total_time": lost_periods_total_time,
        "total_availability_reductions_by_one": lost_periods_total_availability_reductions_by_one,
        "instances": lost_period_effects
    },
    "added_periods_effects": {
        "total_time": added_periods_total_time,
        "total_availability_increases_by_one": added_periods_total_availability_increases_by_one,
        "instances": added_period_effects
    },
    "available_sat_diffs": available_sat_diffs
}

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)