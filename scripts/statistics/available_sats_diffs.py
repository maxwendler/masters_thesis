import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("ref_mobility_availables_json")
parser.add_argument("new_mobility_availables_json")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.ref_mobility_availables_json, "r") as json_f:
    ref_availability_stats = json.load(json_f)

with open(args.new_mobility_availables_json, "r") as json_f:
    new_availability_stats = json.load(json_f)

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

output = {
    "avg_abs_sat_num_diff": abs_diff_sum / len(available_sat_diffs),
    "time_with_num_diff_to_total_time": times_with_num_diff / len(available_sat_diffs),
    "availability_num_time_diffs": availability_num_time_diffs,
    "availability_num_ratio_diffs": availability_num_ratio_diffs,
    "available_sat_diffs": available_sat_diffs
}

with open(args.output_path, "w") as out_json:
    json.dump(output, out_json, indent=4)