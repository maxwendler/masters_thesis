import argparse
import json
import os

parser = argparse.ArgumentParser(prog="summarize_comm_comp_info.py")
parser.add_argument("comp_info_dir")
parser.add_argument("output_path")
args = parser.parse_args()

comp_info_dir = args.comp_info_dir if args.comp_info_dir.endswith("/") else args.comp_info_dir + "/"
info_json_paths = [ comp_info_dir + fname for fname in list( filter( lambda fname: fname.endswith("_communication_comparison.json"), os.listdir(comp_info_dir) ) ) ] 

mobilities = info_json_paths[0].split("/")[-1].split("_")[0].split("-")
ref_mobility = mobilities[0]
new_mobility = mobilities[1]

coverages = []
exclusions = []
total_excluded_time_to_ref_times = []

for path in info_json_paths:

    comm_periods = {}
    with open(path, "r") as json_f:
        comm_periods = json.load(json_f)
    
    for period_group in comm_periods["period_groups"]:
        coverages.append(period_group["ref_coverage"])
        exclusions.append(period_group["new_excluded"])

    for unmatched_period in comm_periods["unmatched_periods"]:
        if ref_mobility in unmatched_period.keys():
            coverages.append(period_group["ref_coverage"])
        
        if new_mobility in unmatched_period.keys():
            exclusions.append(period_group["new_excluded"])

    total_excluded_time_to_ref_times.append(comm_periods["total_excluded_time_to_ref_time"])

avg_coverage = sum(coverages) / len(coverages)
avg_exlusion = sum(exclusions) / len(exclusions)
avg_excluded_to_ref = sum(total_excluded_time_to_ref_times) / len(total_excluded_time_to_ref_times)
output = {"avg_ref_coverage": avg_coverage,
          "avg_new_exclusion": avg_exlusion,
          "avg_excluded_time_to_ref_time": avg_excluded_to_ref}

with open(args.output_path, "w") as output_f:
    json.dump(output, output_f)