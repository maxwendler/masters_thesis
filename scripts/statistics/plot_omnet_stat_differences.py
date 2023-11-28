import argparse
import csv
import sys, os
sys.path.append(os.path.join(sys.path[0],"..","plots"))
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
from plot_sat_overlap_stats import get_period_start, get_period_end

def get_mod_differences(csv_path, modname):
    
    with open(csv_path, "r") as diff_f:

        row_reader = csv.reader(diff_f)
        header = row_reader.__next__()
        sec_range = list( range( int(header[1]), int(header[-1]) + 1) )

        for row in row_reader:
            if row[0] == modname:
                return sec_range, [ float(val) for val in row[1:] ]
        
        raise NameError(f"No entries for module {modname} could be found!")

parser = argparse.ArgumentParser(prog="plot_omnet_stat_differences")
parser.add_argument("angles_csv")
parser.add_argument("distances_csv")
parser.add_argument("delays_csv")
parser.add_argument("sim_start_sec", type=int)
parser.add_argument("modname")
parser.add_argument("png_output_path")
parser.add_argument("-c", "--changes", action="store_true")
parser.add_argument("--comm_comp_json")
args = parser.parse_args()

sec_range, angle_diffs_or_changes = get_mod_differences(args.angles_csv, args.modname) 
sec_range, distance_diffs_or_changes = get_mod_differences(args.distances_csv, args.modname)
sec_range, delay_diffs_or_changes = get_mod_differences(args.delays_csv, args.modname)
diff_or_change_str = "change" if args.changes else "difference"

if args.comm_comp_json:

    comm_period_comparison = {}
    with open(args.comm_comp_json, "r") as json_f:
        comm_period_comparison = json.load(json_f)
    
    mobilities = args.comm_comp_json.split("/")[-1].split("_")[0].split("-")
    ref_mobility = mobilities[0]
    new_mobility = mobilities[1]

    period_or_periodgroup_list =  comm_period_comparison["period_groups"] + comm_period_comparison["unmatched_periods"]
    period_or_periodgroup_list.sort(key=lambda p_or_pgroup: get_period_start(p_or_pgroup, ref_mobility, new_mobility))
    row_num = len(period_or_periodgroup_list)

    fig = make_subplots(rows=row_num, cols=3, subplot_titles=[diff_or_change_str + " of elevation angle",
                                                              diff_or_change_str + " of distance to SOP",
                                                              diff_or_change_str + " of delay"] + [""] * (row_num*3 - 1))

    fig.update_layout(showlegend=False)

    fig.add_annotation(dict(font=dict(color="blue",size=14),
                            x=0,
                            y=1.2,
                            showarrow=False,
                            text=f"overlapping periods values",
                            textangle=0,
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="green",size=14),
                            x=0,
                            y=1.15,
                            showarrow=False,
                            text=f"unmatched {ref_mobility} values",
                            textangle=0,
                            xref="paper",
                            yref="paper"))
    
    fig.add_annotation(dict(font=dict(color="orange",size=14),
                            x=0,
                            y=1.1,
                            showarrow=False,
                            text=f"unmatched {new_mobility} values",
                            textangle=0,
                            xref="paper",
                            yref="paper"))

    for p_or_p_group_idx in range(0, len(period_or_periodgroup_list)):
        
        p_or_p_group = period_or_periodgroup_list[p_or_p_group_idx]
        is_p_group = ref_mobility in p_or_p_group.keys() and new_mobility in p_or_p_group.keys()


        plot_start_sec = get_period_start(p_or_p_group, ref_mobility, new_mobility)
        plot_end_sec = get_period_end(p_or_p_group, ref_mobility, new_mobility)
        sec_range = list( range(plot_start_sec, plot_end_sec + 1) )

        local_angle_diffs_or_changes = angle_diffs_or_changes[plot_start_sec - args.sim_start_sec: plot_end_sec + 1 - args.sim_start_sec]
        local_distance_diffs_or_changes = distance_diffs_or_changes[plot_start_sec - args.sim_start_sec: plot_end_sec + 1 - args.sim_start_sec]
        local_delay_diffs_or_changes = delay_diffs_or_changes[plot_start_sec - args.sim_start_sec: plot_end_sec + 1 - args.sim_start_sec]

        color = ""
        if is_p_group:
            color="blue"
        else:
            if ref_mobility in p_or_p_group.keys():
                color="green"
            else:
                color="orange"

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=local_angle_diffs_or_changes,
                    line=dict(color=color)),
            row=p_or_p_group_idx + 1, col=1,
        )

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=local_distance_diffs_or_changes,
                    line=dict(color=color)),
            row=p_or_p_group_idx + 1, col=2,
        )

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=local_delay_diffs_or_changes,
                    line=dict(color=color)),
            row=p_or_p_group_idx + 1, col=3,
        )

else:

    fig = make_subplots(rows=2, cols=1, subplot_titles=[f"{diff_or_change_str} of elevation angle from ref. mobility at sim. second", 
                                                    f"{diff_or_change_str} of distance to SOP from ref. mobility at sim. second"])


    fig.add_trace(
        go.Scatter(x=sec_range, 
                    y=angle_diffs_or_changes),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=sec_range, 
            y=distance_diffs_or_changes),
        row=2, col=1
    )

fig.write_image(args.png_output_path)
html_output_path = args.png_output_path.removesuffix("png") + "html"
fig.write_html(html_output_path)