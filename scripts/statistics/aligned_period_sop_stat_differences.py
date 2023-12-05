import argparse
import json
import numpy as np
from scipy.interpolate import CubicSpline
from plotly.subplots import make_subplots
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="aligned_period_sop_stat_differences", description="???")
parser.add_argument("comm_period_groups_path", help="Path of JSON that matches communication periods between reference mobility and alternative (new) mobility.")
parser.add_argument("ref_mobility", help="Name of reference mobility.")
parser.add_argument("ref_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("new_mobility", help="Name of the alternative (new) mobility.")
parser.add_argument("new_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("output_path", help="Path where result JSON will be written to.")
parser.add_argument("plot_path", help="Path where result plot will be written to.")
parser.add_argument("--changes", action="store_true", help="If flag is set, calculates changes from reference mobility to alternative (new) mobility instead of differences.")
args = parser.parse_args()

### load communication period statistics ###
ref_mobility = args.ref_mobility
ref_mobility_stats = None
with open(args.ref_mobility_periods_path, "r") as in_json:
    ref_mobility_stats = json.load(in_json)
new_mobility = args.new_mobility
new_mobility_stats = None
with open(args.new_mobility_periods_path, "r") as in_json:
    new_mobility_stats = json.load(in_json)

# load communication period comparison
comm_periods = {}
with open(args.comm_period_groups_path, "r") as in_json:
    comm_periods = json.load(in_json)

period_groups = comm_periods["period_groups"]
row_num = len(period_groups)

fig = None
# nothing to display: just add that as text in figure
if not row_num > 0:
    fig = go.Figure()

    fig.add_annotation(dict(font=dict(color="black",size=40),
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        text="No common communication periods to display.",
                        textangle=0,
                        xref="paper",
                        yref="paper"))

else:
    fig = make_subplots(rows=row_num, cols=3)   
    fig.update_layout(showlegend=False)

    #annotations identifying plot line color with respective mobility or differences/changes
    fig.add_annotation(dict(font=dict(color="red",size=14),
                            x=0,
                            y=1.15,
                            showarrow=False,
                            text=f"{ref_mobility} values",
                            textangle=0,
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="blue",size=14),
                            x=0,
                            y=1.1,
                            showarrow=False,
                            text=f"{new_mobility} values",
                            textangle=0,
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="green",size=14),
                            x=0,
                            y=1.05,
                            showarrow=False,
                            text="changes" if args.changes else "differences",
                            textangle=0,
                            xref="paper",
                            yref="paper"))

output = {"modname": comm_periods["modname"],
          "period_groups": []}

for p_group_idx in range(len(period_groups)):
    
    p_group = period_groups[p_group_idx]
    sec_range = list( range( p_group[ref_mobility]["period"][0], p_group[ref_mobility]["period"][1] + 1) )
    plot_row_idx = p_group_idx + 1
    
    # copy period start and end and mobility period idx
    new_p_group_dict = {ref_mobility: p_group[ref_mobility],
                        new_mobility: p_group[new_mobility]}

    # angles
    # interpolate new to length of ref  
    ref_angles = ref_mobility_stats["angles"][ p_group[ref_mobility]["period_idx"] ]
    ref_xs = np.linspace(0, 1, len(ref_angles))
    new_angles = new_mobility_stats["angles"][ p_group[new_mobility]["period_idx"] ]
    new_xs = np.linspace(0, 1, len(new_angles))

    angle_interpolator = CubicSpline(new_xs, new_angles)
    new_angles_interp = angle_interpolator(ref_xs)

    angle_diffs_or_changes = []
    for i in range(len(ref_angles)):
        if args.changes:
            angle_diffs_or_changes.append( new_angles_interp[i] - ref_angles[i] )
        else:
            angle_diffs_or_changes.append( abs(new_angles_interp[i] - ref_angles[i]) )

    if args.changes:
        new_p_group_dict["angle_changes"] = angle_diffs_or_changes
    else:
        new_p_group_dict["angle_differences"] = angle_diffs_or_changes

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=ref_angles,
                line=dict(color='Red')),
        row=plot_row_idx, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=new_angles_interp,
                line=dict(color='Blue')),
        row=plot_row_idx, col=1
    )

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=angle_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=1
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=1)
    fig.update_yaxes(title_text="elevation angle in °", row=plot_row_idx, col=1)

    # distances
    # interpolate new to length of ref 
    ref_distances = ref_mobility_stats["distances"][ p_group[ref_mobility]["period_idx"] ]
    new_distances = new_mobility_stats["distances"][ p_group[new_mobility]["period_idx"] ]

    distance_interpolator = CubicSpline(new_xs, new_distances)
    new_distances_interp = distance_interpolator(ref_xs)

    distance_diffs_or_changes = []
    for i in range(len(ref_distances)):
        if args.changes:
            distance_diffs_or_changes.append( new_distances_interp[i] - ref_distances[i] )
        else:
            distance_diffs_or_changes.append( abs(new_distances_interp[i] - ref_distances[i]) )

    if args.changes:
        new_p_group_dict["distance_changes"] = distance_diffs_or_changes
    else:
        new_p_group_dict["distance_differences"] = distance_diffs_or_changes

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=ref_distances,
                line=dict(color='Red')),
        row=plot_row_idx, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=new_distances_interp,
                line=dict(color='Blue')),
        row=plot_row_idx, col=2
    )

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=distance_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=2
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=2)
    fig.update_yaxes(title_text="distance in km", row=plot_row_idx, col=2)

    # delays
    # interpolate new to length of ref 
    ref_delays = ref_mobility_stats["delays"][ p_group[ref_mobility]["period_idx"] ]
    new_delays = new_mobility_stats["delays"][ p_group[new_mobility]["period_idx"] ]

    delay_interpolator = CubicSpline(new_xs, new_delays)
    new_delays_interp = delay_interpolator(ref_xs)

    delay_diffs_or_changes = []
    for i in range(len(ref_delays)):
        if args.changes:
            delay_diffs_or_changes.append( new_delays_interp[i] - ref_delays[i] )
        else:
            delay_diffs_or_changes.append( abs(new_delays_interp[i] - ref_delays[i]) )

    if args.changes:
        new_p_group_dict["delay_changes"] = delay_diffs_or_changes
    else:
        new_p_group_dict["delay_differences"] = delay_diffs_or_changes

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=ref_delays,
                line=dict(color='Red')),
        row=plot_row_idx, col=3
    )
    
    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=new_delays_interp,
                line=dict(color='Blue')),
        row=plot_row_idx, col=3
    )

    fig.add_trace(
        go.Scatter(x=sec_range, 
                y=delay_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=3
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=3)
    fig.update_yaxes(title_text="delay in ms", row=plot_row_idx, col=3)

    output["period_groups"].append(new_p_group_dict)

with open(args.output_path, "w") as out_f:
    json.dump(output, out_f, indent=4)

fig.write_image(args.plot_path, width=1920, height=1080)