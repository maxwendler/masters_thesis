import argparse
import json
import os
from statistics import median

parser = argparse.ArgumentParser(prog="summarize_comm_comp_info.py")
parser.add_argument("comp_info_dir", help="Path of directory with all the *_communication_comparison.json files of a constellation.")
parser.add_argument("output_path")
args = parser.parse_args()

comp_info_dir = args.comp_info_dir if args.comp_info_dir.endswith("/") else args.comp_info_dir + "/"
# create paths of JSON files in comp_info_dir
info_json_paths = [ comp_info_dir + fname for fname in list( filter( lambda fname: fname.endswith("_communication_comparison.json"), os.listdir(comp_info_dir) ) ) ] 

mobilities = info_json_paths[0].split("/")[-1].split("_")[0].split("-")
ref_mobility = mobilities[0]
new_mobility = mobilities[1]

coverages = []
exclusions = []
duration_changes = []
zenith_shifts = []
total_excluded_time_to_ref_times = []
unmatched_ref_periods_num = 0
unmatched_new_periods_num = 0

# collect coverage, exclusion and excluded_time_to_ref_time values for averaging
for path in info_json_paths:

    comm_periods = {}
    with open(path, "r") as json_f:
        comm_periods = json.load(json_f)
    
    for period_group in comm_periods["period_groups"]:
        coverages.append(period_group["ref_coverage"])
        exclusions.append(period_group["new_excluded"])
        duration_changes.append(period_group["duration_change"])
        zenith_shifts.append(period_group["zenith_shift"])

    for unmatched_period in comm_periods["unmatched_periods"]:
        if ref_mobility in unmatched_period.keys():
            coverages.append(period_group["ref_coverage"])
            unmatched_ref_periods_num += 1

        if new_mobility in unmatched_period.keys():
            exclusions.append(period_group["new_excluded"])
            unmatched_new_periods_num += 1

    total_excluded_time_to_ref_times.append(comm_periods["total_excluded_time_to_ref_time"])

# calculate averages
avg_coverage = sum(coverages) / len(coverages)
avg_exlusion = sum(exclusions) / len(exclusions)
avg_excluded_to_ref = sum(total_excluded_time_to_ref_times) / len(total_excluded_time_to_ref_times)
min_zenith_shift = min(zenith_shifts)
max_zenith_shift = max(zenith_shifts)
avg_zenith_shift = sum(zenith_shifts) / len(zenith_shifts)
median_zenith_shift = median(zenith_shifts)
min_duration_change = min(duration_changes)
max_duration_change = max(duration_changes)
avg_duration_change = sum(duration_changes) / len(duration_changes)
median_duration_change = median(duration_changes)

output = {"avg_ref_coverage": avg_coverage,
          "avg_new_exclusion": avg_exlusion,
          "avg_excluded_time_to_ref_time": avg_excluded_to_ref,
          "unmatched_ref_periods": unmatched_ref_periods_num,
          "unmatched_new_periods": unmatched_new_periods_num,
          "min_zenith_shift": min_zenith_shift,
          "max_zenith_shift": max_zenith_shift,
          "avg_zenith_shift": avg_zenith_shift,
          "median_zenith_shift": median_zenith_shift,
          "min_duration_change": min_duration_change,
          "max_duration_change": max_duration_change,
          "avg_duration_change": avg_duration_change,
          "median_duration_change": median_duration_change}

with open(args.output_path, "w") as output_f:
    json.dump(output, output_f, indent=4)