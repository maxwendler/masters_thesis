import argparse
import json
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_zenith_interval_diff_at_offset_sum")
parser.add_argument("zenith_interval_changes_json")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.zenith_interval_changes_json, "r") as json_f:
    zenith_interval_changes = json.load(json_f)

interval_differences = [abs(interval_change) for interval_change in zenith_interval_changes["same_periods_changes"].values()]
offset_sums = list(zenith_interval_changes["same_periods_abs_offset_sums"].values())

fig = go.Figure(data=go.Scatter(x=offset_sums, y=interval_differences, mode='lines+markers'))

fig.update_xaxes(title_text='seconds sum to epoch')
fig.update_yaxes(title_text='absolute interval difference in seconds')

fig.write_image(args.output_path)