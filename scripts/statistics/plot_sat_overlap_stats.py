import argparse
import json
import plotly.express as px

def get_period_start(period_group_or_period_dict: dict, ref_mobility, new_mobility):

    if ref_mobility in period_group_or_period_dict.keys() and new_mobility in period_group_or_period_dict.keys():
        return min(period_group_or_period_dict[ref_mobility]["period"][0], period_group_or_period_dict[new_mobility]["period"][0])
    
    else:
        if ref_mobility in period_group_or_period_dict.keys():
            return period_group_or_period_dict[ref_mobility]["period"][0]
        else:
            return period_group_or_period_dict[new_mobility]["period"][0]


parser = argparse.ArgumentParser(prog="plot_sat_overlap_stats", description="Creates a bar chart where for every (overlapping and non-overlapping) communication period of the reference and the new mobility a bar with two components is plotted: (1) Coverage of reference period, (2) Exclusion of new period.")
parser.add_argument("comm_comp_json_path")
args = parser.parse_args()

mobilities = args.comm_comp_json_path.split("/")[-1].split("_")[0].split("-")
ref_mobility = mobilities[0]
new_mobility = mobilities[1]

comm_periods = None
with open(args.comm_comp_json_path, "r") as json_f:
    comm_periods = json.load(json_f)

# sort dicts of period groups and unmatched periods in time order
periods_list = comm_periods["period_groups"] + comm_periods["unmatched periods"]
periods_list.sort(key=lambda p_dict: get_period_start(p_dict, ref_mobility, new_mobility))

x_labels = []
ref_coverage_labels = []
ref_coverage_vals = []

for period_dict in periods_list:
    
    if "multiple_matches" in period_dict.keys():
        if period_dict["multiple_matches"]:
            raise ValueError("Can't plot period groups with multiple matches yet!")

    start_sec = None
    end_sec = None
    if ref_mobility in period_dict.keys() and new_mobility in period_dict.keys():
        start_sec = min( period_dict[ref_mobility]["period"][0], period_dict[new_mobility]["period"][0] )
        end_sec = max( period_dict[ref_mobility]["period"][1], period_dict[new_mobility]["period"][1])
    else:
        if ref_mobility in period_dict.keys():
            start_sec = period_dict[ref_mobility]["period"][0]
            end_sec = period_dict[ref_mobility]["period"][1]
        else:
            start_sec = period_dict[new_mobility]["period"][0]
            end_sec = period_dict[new_mobility]["period"][1]

    ref_coverage = period_dict["ref_coverage"]
    new_excluded = period_dict["new_excluded"]

    x_labels += [f"{start_sec}s to {end_sec}s"] * 2
    ref_coverage_labels += ["ref_coverage", "new_exclusion"]
    ref_coverage_vals += [ref_coverage, new_excluded]

fig = px.bar(x=x_labels, y=ref_coverage_vals, color=ref_coverage_labels)
output_path = args.comm_comp_json_path.removesuffix("communication_comparison.json") + "overlaps.png"
fig.write_image(output_path)