import argparse
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_comm_comparison.py", description="???")
parser.add_argument("comm_periods_path")
parser.add_argument("ref_mobility")
parser.add_argument("ref_mobility_stats_path")
parser.add_argument("new_mobility")
parser.add_argument("new_mobility_stats_path")
args = parser.parse_args()

output_path_base = args.comm_periods_path.removesuffix(".json")

ref_mobility = args.ref_mobility
ref_mobility_stats = None
with open(args.ref_mobility_stats_path, "r") as in_json:
    ref_mobility_stats = json.load(in_json)

new_mobility = args.new_mobility
new_mobility_stats = None
with open(args.new_mobility_stats_path, "r") as in_json:
    new_mobility_stats = json.load(in_json)

comm_periods = {}
with open(args.comm_periods_path, "r") as in_json:
    comm_periods = json.load(in_json)

period_groups = comm_periods["period_groups"]

row_num = len(period_groups)
# rows: period groups, columns: angles, distances, delays
fig = make_subplots(rows=row_num, cols=3)   
fig.update_layout(showlegend=False)

fig.add_annotation(dict(font=dict(color="red",size=14),
                        x=0,
                        y=1.1,
                        showarrow=False,
                        text=f"{ref_mobility} values",
                        textangle=0,
                        xref="paper",
                        yref="paper"))

fig.add_annotation(dict(font=dict(color="blue",size=14),
                        x=0,
                        y=1.05,
                        showarrow=False,
                        text=f"{new_mobility} values",
                        textangle=0,
                        xref="paper",
                        yref="paper"))

for period_group_idx in range(0, len(period_groups)):
    plot_row_idx = period_group_idx + 1

    period_group = period_groups[period_group_idx]

    ref_period_idx = period_group[ref_mobility]["period_idx"]
    new_period_idx = period_group[new_mobility]["period_idx"]

    start_sec = min(period_group[ref_mobility]["period"][0], period_group[new_mobility]["period"][0])
    end_sec = max(period_group[ref_mobility]["period"][1], period_group[new_mobility]["period"][1])
    sec_range = list( range(start_sec, end_sec) )
    
    ref_vals_start_padding = []
    if period_group[ref_mobility]["period"][0] > period_group[new_mobility]["period"][0]:
        ref_vals_start_padding = [0] * (period_group[ref_mobility]["period"][0] - period_group[new_mobility]["period"][0]) 
    
    ref_vals_end_padding = []
    if period_group[ref_mobility]["period"][1] < period_group[new_mobility]["period"][1]:
        ref_vals_end_padding = [0] * (period_group[new_mobility]["period"][1] - period_group[ref_mobility]["period"][1])
    
    new_vals_start_padding = []
    if period_group[new_mobility]["period"][0] > period_group[ref_mobility]["period"][0]:
        new_vals_start_padding = [0] * (period_group[new_mobility]["period"][0] - period_group[ref_mobility]["period"][0]) 
    
    new_vals_end_padding = []
    if period_group[new_mobility]["period"][1] < period_group[ref_mobility]["period"][1]:
        new_vals_end_padding = [0] * (period_group[ref_mobility]["period"][1] - period_group[new_mobility]["period"][1])

    ref_vals_len = len(ref_vals_start_padding) + (period_group[ref_mobility]["period"][1] - period_group[ref_mobility]["period"][0]) + len(ref_vals_end_padding)
    new_vals_len = len(new_vals_start_padding) + (period_group[new_mobility]["period"][1] - period_group[new_mobility]["period"][0]) + len(new_vals_end_padding)

    if ref_vals_len != new_vals_len:
        raise ValueError(f"Array of reference mobility values with padding has different length than array of new mobility values with padding ({ref_vals_len} to {new_vals_len})")

    # line plots of elevation angles
    ref_angles = ref_vals_start_padding + ref_mobility_stats["angles"][ref_period_idx] + ref_vals_end_padding
    new_angles = new_vals_start_padding + new_mobility_stats["angles"][new_period_idx] + new_vals_end_padding

    ref_angles_dict = {"sim. second": sec_range, "elevation angle in °": ref_angles}
    new_angles_dict = {"sim. second": sec_range, "elevation angle in °": new_angles}

    fig.add_trace(
        go.Scatter(x=ref_angles_dict["sim. second"], 
                   y=ref_angles_dict["elevation angle in °"],
                   line=dict(color='Red')),
        row=plot_row_idx, col=1,
    )
    
    fig.add_trace(
        go.Scatter(x=new_angles_dict["sim. second"], 
                   y=new_angles_dict["elevation angle in °"],
                   line=dict(color='Blue')),
        row=plot_row_idx, col=1,
    )

    # line plots of distances
    ref_distances = ref_vals_start_padding + ref_mobility_stats["distances"][ref_period_idx] + ref_vals_end_padding
    new_distances = new_vals_start_padding + new_mobility_stats["distances"][new_period_idx] + new_vals_end_padding

    ref_distances_dict = {"sim. second": sec_range, "distance in km": ref_distances}
    new_distances_dict = {"sim. second": sec_range, "distance in km": new_distances}

    fig.add_trace(
        go.Scatter(x=ref_distances_dict["sim. second"], 
                   y=ref_distances_dict["distance in km"],
                   line=dict(color='Red')),
        row=plot_row_idx, col=2,
    )
    
    fig.add_trace(
        go.Scatter(x=new_distances_dict["sim. second"], 
                   y=new_distances_dict["distance in km"],
                   line=dict(color='Blue')),
        row=plot_row_idx, col=2,
    )

    # line plots of propagation delays
    ref_delays = ref_vals_start_padding + ref_mobility_stats["delays"][ref_period_idx] + ref_vals_end_padding
    new_delays = new_vals_start_padding + new_mobility_stats["delays"][new_period_idx] + new_vals_end_padding

    ref_delays_dict = {"sim. second": sec_range, "delay in s": ref_delays}
    new_delays_dict = {"sim. second": sec_range, "delay in s": new_delays}

    fig.add_trace(
        go.Scatter(x=ref_delays_dict["sim. second"], 
                   y=ref_delays_dict["delay in s"],
                   line=dict(color='Red')),
        row=plot_row_idx, col=3,
    )
    
    fig.add_trace(
        go.Scatter(x=new_delays_dict["sim. second"], 
                   y=new_delays_dict["delay in s"],
                   line=dict(color='Blue')),
        row=plot_row_idx, col=3,
    )

fig.write_image(output_path_base + ".png", width=1920, height=1080)
fig.write_html(output_path_base + ".html")