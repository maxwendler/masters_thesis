import argparse
import json
import os
import plotly.graph_objects as go

parser = argparse.ArgumentParser()
parser.add_argument("grouped_periods_json")
parser.add_argument("angle_interval", type=int)
parser.add_argument("new_mobility")
parser.add_argument("delay_diffs_output_dir")
parser.add_argument("duration_diffs_output_dir")
args = parser.parse_args()

delay_diffs_output_dir = args.delay_diffs_output_dir if args.delay_diffs_output_dir.endswith("/") else args.delay_diffs_output_dir + "/"
duration_diffs_output_dir = args.duration_diffs_output_dir if args.duration_diffs_output_dir.endswith("/") else args.duration_diffs_output_dir + "/"
os.makedirs(delay_diffs_output_dir, exist_ok=True)
os.makedirs(duration_diffs_output_dir, exist_ok=True)

with open(args.grouped_periods_json, "r") as json_f:
    grouped_periods = json.load(json_f)

group_names = []
grouped_avg_delay_diffs = []
grouped_duration_diffs = []
for interval_factor_str in sorted(list(grouped_periods.keys()), key=lambda int_str: int(int_str)):
    
    interval_factor = int(interval_factor_str)
    interval_start_angle = interval_factor * args.angle_interval
    interval_end_angle = (interval_factor + 1) * args.angle_interval

    periods = grouped_periods[interval_factor_str]
    for p in periods:
        group_names.append(f"{str(interval_start_angle)} to {str(interval_end_angle)} °")
        grouped_avg_delay_diffs.append(p["period_group"]["delay_differences_avg"])
        grouped_duration_diffs.append( abs( (p["period_group"]["sgp4"]["period"][1] - p["period_group"]["sgp4"]["period"][0]) - (p["period_group"][args.new_mobility]["period"][1] - p["period_group"][args.new_mobility]["period"][0]) ) )

fig = go.Figure(data=go.Scatter(x=group_names, y=grouped_avg_delay_diffs, name="avg. delay difference", mode='markers'))
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=sorted(list(set(group_names)))
    )
)
fig.write_image(delay_diffs_output_dir + "sgp4-" + args.new_mobility +"_all_groups_delay_differences.svg")

fig = go.Figure(data=go.Scatter(x=group_names, y=grouped_duration_diffs, name="duration differences", mode='markers'))
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=sorted(list(set(group_names))),
        tickangle=-90
    )
)
fig.write_image(duration_diffs_output_dir + "sgp4-" + args.new_mobility + "_all_groups_duration_differences.svg")