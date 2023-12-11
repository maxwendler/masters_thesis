import argparse
import json
import os
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
    plot_row_idx = p_group_idx + 1
    ref_sec_range = list(range(p_group[ref_mobility]["period"][0], p_group[ref_mobility]["period"][1] + 1))
    aligned_new_sec_range = list(range(p_group[new_mobility]["period"][0] - p_group["zenith_shift"], p_group[new_mobility]["period"][1] - p_group["zenith_shift"] + 1))

    # copy period start and end and mobility period idx for mobilities, and offset to TLE epoch of ref
    new_p_group_dict = {ref_mobility: p_group[ref_mobility],
                        new_mobility: p_group[new_mobility],
                        "ref_start_to_epoch_offset": p_group["ref_start_to_epoch_offset"]}

    # angles  
    ref_angles = ref_mobility_stats["angles"][ p_group[ref_mobility]["period_idx"] ]
    new_angles = new_mobility_stats["angles"][ p_group[new_mobility]["period_idx"] ]

    duration_difference = abs(len(ref_angles) - len(new_angles))
    diff_start_idx = 0
    if duration_difference % 2 == 1:
        diff_start_idx += 1
        duration_difference -= 1
    diff_start_idx += int(duration_difference / 2)

    # only calc differences / changes in overlapping duration
    # i.e. starting at idx duration_difference/2 (+1 for odd difference to len - duration_difference/2
    
    angle_diffs_or_changes = []
    diff_sec_range = None
    # fully use ref_angles, use slice of new_angles
    if len(ref_angles) < len(new_angles):
        aligned_overlap_new_angles = new_angles[diff_start_idx:( len(new_angles) - int(duration_difference/2))]
        
        # as aligned to ref_mobility period 
        diff_sec_range = ref_sec_range        
    
        for i in range(len(ref_angles)):
            if args.changes:
                angle_diffs_or_changes.append( aligned_overlap_new_angles[i] - ref_angles[i] )
            else:
                angle_diffs_or_changes.append( abs(aligned_overlap_new_angles[i] - ref_angles[i]) )
    
    # fully use new_angles, use slice of ref_angles
    elif len(new_angles) < len(ref_angles):
        aligned_overlap_ref_angles = ref_angles[diff_start_idx:( len(ref_angles) - int(duration_difference/2))]

        diff_sec_range = aligned_new_sec_range

        for i in range(len(new_angles)):
            if args.changes:
                angle_diffs_or_changes.append( new_angles[i] - aligned_overlap_ref_angles[i] )
            else:
                angle_diffs_or_changes.append( abs(new_angles[i] - aligned_overlap_ref_angles[i]) )

    # no duration difference
    else:
        diff_sec_range = ref_sec_range
        for i in range(len(new_angles)):
            if args.changes:
                angle_diffs_or_changes.append( new_angles[i] - ref_angles[i] )
            else:
                angle_diffs_or_changes.append( abs(new_angles[i] - ref_angles[i]) )

    angle_diffs_or_changes_avg = sum(angle_diffs_or_changes) / len(angle_diffs_or_changes)
    angle_diffs_or_changes_max = max(angle_diffs_or_changes)

    if args.changes:
        new_p_group_dict["angle_changes"] = angle_diffs_or_changes
        new_p_group_dict["angle_changes_avg"] = angle_diffs_or_changes_avg
        new_p_group_dict["angle_changes_max"] = angle_diffs_or_changes_max
    else:
        new_p_group_dict["angle_differences"] = angle_diffs_or_changes
        new_p_group_dict["angle_differences_avg"] = angle_diffs_or_changes_avg
        new_p_group_dict["angle_differences_max"] = angle_diffs_or_changes_max
    
    fig.add_trace(
        go.Scatter(x=ref_sec_range, 
                y=ref_angles,
                line=dict(color='Red')),
        row=plot_row_idx, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=aligned_new_sec_range, 
                y=new_angles,
                line=dict(color='Blue')),
        row=plot_row_idx, col=1
    )

    fig.add_trace(
        go.Scatter(x=diff_sec_range, 
                y=angle_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=1
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=1)
    fig.update_yaxes(title_text="elevation angle in °", row=plot_row_idx, col=1)

    # distances 
    ref_distances = ref_mobility_stats["distances"][ p_group[ref_mobility]["period_idx"] ]
    new_distances = new_mobility_stats["distances"][ p_group[new_mobility]["period_idx"] ]
    
    distance_diffs_or_changes = []
    if len(ref_distances) < len(new_distances):
        aligned_overlap_new_distances = new_distances[diff_start_idx:( len(new_distances) - int(duration_difference/2))]    
    
        for i in range(len(ref_distances)):
            if args.changes:
                distance_diffs_or_changes.append( aligned_overlap_new_distances[i] - ref_distances[i] )
            else:
                distance_diffs_or_changes.append( abs(aligned_overlap_new_distances[i] - ref_distances[i]) )
    
    elif len(new_distances) < len(ref_distances):
        aligned_overlap_ref_distances = ref_distances[diff_start_idx:( len(ref_distances) - int(duration_difference/2))]

        for i in range(len(new_distances)):
            if args.changes:
                distance_diffs_or_changes.append( new_distances[i] - aligned_overlap_ref_distances[i] )
            else:
                distance_diffs_or_changes.append( abs(new_distances[i] - aligned_overlap_ref_distances[i]) )

    else:
        for i in range(len(new_distances)):
            if args.changes:
                distance_diffs_or_changes.append( new_distances[i] - ref_distances[i] )
            else:
                distance_diffs_or_changes.append( abs(new_distances[i] - ref_distances[i]) )

    distance_diffs_or_changes_avg = sum(distance_diffs_or_changes) / len(distance_diffs_or_changes)
    distance_diffs_or_changes_max = max(distance_diffs_or_changes)

    if args.changes:
        new_p_group_dict["distance_changes"] = distance_diffs_or_changes
        new_p_group_dict["distance_changes_avg"] = distance_diffs_or_changes_avg
        new_p_group_dict["distance_changes_max"] = distance_diffs_or_changes_max
    else:
        new_p_group_dict["distance_differences"] = distance_diffs_or_changes
        new_p_group_dict["distance_differences_avg"] = distance_diffs_or_changes_avg
        new_p_group_dict["distance_differences_max"] = distance_diffs_or_changes_max

    fig.add_trace(
        go.Scatter(x=ref_sec_range, 
                y=ref_distances,
                line=dict(color='Red')),
        row=plot_row_idx, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=aligned_new_sec_range, 
                y=new_distances,
                line=dict(color='Blue')),
        row=plot_row_idx, col=2
    )

    fig.add_trace(
        go.Scatter(x=diff_sec_range, 
                y=distance_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=2
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=2)
    fig.update_yaxes(title_text="distance in km", row=plot_row_idx, col=2)

    # delays 
    ref_delays = ref_mobility_stats["delays"][ p_group[ref_mobility]["period_idx"] ]
    new_delays = new_mobility_stats["delays"][ p_group[new_mobility]["period_idx"] ]


    delay_diffs_or_changes = []
    if len(ref_delays) < len(new_delays):
        aligned_overlap_new_delays = new_delays[diff_start_idx:( len(new_delays) - int(duration_difference/2))]    
    
        for i in range(len(ref_delays)):
            if args.changes:
                delay_diffs_or_changes.append( aligned_overlap_new_delays[i] - ref_delays[i] )
            else:
                delay_diffs_or_changes.append( abs(aligned_overlap_new_delays[i] - ref_delays[i]) )
    
    elif len(new_delays) < len(ref_delays):
        aligned_overlap_ref_delays = ref_delays[diff_start_idx:( len(ref_delays) - int(duration_difference/2))]

        for i in range(len(new_delays)):
            if args.changes:
                delay_diffs_or_changes.append( new_delays[i] - aligned_overlap_ref_delays[i] )
            else:
                delay_diffs_or_changes.append( abs(new_delays[i] - aligned_overlap_ref_delays[i]) )

    else:
        for i in range(len(new_delays)):
            if args.changes:
                delay_diffs_or_changes.append( new_delays[i] - ref_delays[i] )
            else:
                delay_diffs_or_changes.append( abs(new_delays[i] - ref_delays[i]) )

    delay_diffs_or_changes_avg = sum(delay_diffs_or_changes) / len(delay_diffs_or_changes)
    delay_diffs_or_changes_max = max(delay_diffs_or_changes)

    if args.changes:
        new_p_group_dict["delay_changes"] = delay_diffs_or_changes
        new_p_group_dict["delay_changes_avg"] = delay_diffs_or_changes_avg
        new_p_group_dict["delay_changes_max"] = delay_diffs_or_changes_max
    else:
        new_p_group_dict["delay_differences"] = delay_diffs_or_changes
        new_p_group_dict["delay_differences_avg"] = delay_diffs_or_changes_avg
        new_p_group_dict["delay_differences_max"] = delay_diffs_or_changes_max

    fig.add_trace(
        go.Scatter(x=ref_sec_range, 
                y=ref_delays,
                line=dict(color='Red')),
        row=plot_row_idx, col=3
    )
    
    fig.add_trace(
        go.Scatter(x=aligned_new_sec_range, 
                y=new_delays,
                line=dict(color='Blue')),
        row=plot_row_idx, col=3
    )

    fig.add_trace(
        go.Scatter(x=diff_sec_range, 
                y=delay_diffs_or_changes,
                line=dict(color='Green')),
        row=plot_row_idx, col=3
    )

    fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=3)
    fig.update_yaxes(title_text="delay in ms", row=plot_row_idx, col=3)

    output["period_groups"].append(new_p_group_dict)

os.makedirs("/".join(args.output_path.split("/")[:-1]), exist_ok=True)
os.makedirs("/".join(args.plot_path.split("/")[:-1]), exist_ok=True)

with open(args.output_path, "w") as out_f:
    json.dump(output, out_f, indent=4)

fig.write_image(args.plot_path, width=1920, height=1080)