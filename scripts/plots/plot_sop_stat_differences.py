"""
Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import argparse
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import sys, os
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import get_mod_row 

def get_period_start(period_group_or_period_dict: dict, ref_mobility, new_mobility):

    if ref_mobility in period_group_or_period_dict.keys() and new_mobility in period_group_or_period_dict.keys():
        return min(period_group_or_period_dict[ref_mobility]["period"][0], period_group_or_period_dict[new_mobility]["period"][0])
    
    else:
        if ref_mobility in period_group_or_period_dict.keys():
            return period_group_or_period_dict[ref_mobility]["period"][0]
        else:
            return period_group_or_period_dict[new_mobility]["period"][0]

def get_period_end(period_group_or_period_dict: dict, ref_mobility, new_mobility):

    if ref_mobility in period_group_or_period_dict.keys() and new_mobility in period_group_or_period_dict.keys():
        return max(period_group_or_period_dict[ref_mobility]["period"][1], period_group_or_period_dict[new_mobility]["period"][1])
    
    else:
        if ref_mobility in period_group_or_period_dict.keys():
            return period_group_or_period_dict[ref_mobility]["period"][1]
        else:
            return period_group_or_period_dict[new_mobility]["period"][1]

parser = argparse.ArgumentParser(prog="plot_omnet_stat_differences",
                                 description="""Plots line plots of differences or changes for elevation angles, distances and delays relative to SOP for the specified reference mobility,
                                alternative (new) mobility, constellation and satellite module name. With a communcation comparison JSON path, the plots only show overlapping and unmatched communication 
                                periods of both mobilities.""")
parser.add_argument("angles_csv", help="Path of CSV with elevation angle differences between the two mobilities.")
parser.add_argument("distances_csv", help="Path of CSV with distance differences between the two mobilities.")
parser.add_argument("delays_csv", help="Path of CSV with delay differences between the two mobilities.")
parser.add_argument("sim_start_sec", type=int)
parser.add_argument("modname")
parser.add_argument("img_output_path")
parser.add_argument("-c", "--changes", action="store_true", help="Plots positive or negative changes instead of differences")
parser.add_argument("--comm_comp_json", help="Path of a communication comparison JSON with which only overlapping and unmatched communication periods are plotted.")
args = parser.parse_args()

angle_diffs_or_changes, sec_range = get_mod_row(args.angles_csv, args.modname) 
distance_diffs_or_changes, sec_range = get_mod_row(args.distances_csv, args.modname)
delay_diffs_or_changes, sec_range = get_mod_row(args.delays_csv, args.modname)
diff_or_change_str = "change" if args.changes else "difference"

# local plots
if args.comm_comp_json:

    comm_period_comparison = {}
    with open(args.comm_comp_json, "r") as json_f:
        comm_period_comparison = json.load(json_f)
    
    mobilities = args.comm_comp_json.split("/")[-1].split("_")[0].split("-")
    ref_mobility = mobilities[0]
    new_mobility = mobilities[1]

    period_or_periodgroup_list =  comm_period_comparison["period_groups"] + comm_period_comparison["unmatched_periods"]
    # sort periods and period groups by theit start time
    period_or_periodgroup_list.sort(key=lambda p_or_pgroup: get_period_start(p_or_pgroup, ref_mobility, new_mobility))
    # one row of angles, distances, delays per period or period group
    row_num = len(period_or_periodgroup_list)

    if row_num == 0:    
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

        # only have subplot titles for first row as titles for whole column
        fig = make_subplots(rows=row_num, cols=3, subplot_titles=[diff_or_change_str + " of elevation angle",
                                                                diff_or_change_str + " of distance to SOP",
                                                                diff_or_change_str + " of delay"] + [""] * (row_num*3 - 1))

        fig.update_layout(showlegend=False)

        # add annotations identifying colors with overlapping period values, unmatched ref mobility periods and unmatched new mobility periods
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

# full simulation time plots
else:

    fig = make_subplots(rows=3, cols=1, subplot_titles=[f"{diff_or_change_str} of elevation angle from ref. mobility at sim. second", 
                                                    f"{diff_or_change_str} of distance to SOP from ref. mobility at sim. second",
                                                    f"{diff_or_change_str} of delay to SOP from ref. mobility at sim. second"])

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

    fig.add_trace(
        go.Scatter(x=sec_range, 
            y=delay_diffs_or_changes),
        row=3, col=1
    )

fig.write_image(args.img_output_path)
html_output_path = args.img_output_path.removesuffix("svg") + "html"
fig.write_html(html_output_path)