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
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_comm_comparison.py", 
                                 description="""Plots line plots for elevation angles, distances and delays relative to the SOP in the overlapping communication periods of the 
                                specified reference mobility, alternative (new) mobility, constellation and satellite module name.\n
                                Each plot contains a line for the reference mobility and one line for the alternative mobility. To clearly show where communication
                                periods start and end, values outside of the respective periods are set to 0.""")
parser.add_argument("comm_period_groups_path", help="Path of JSON that matches communication periods between reference mobility and alternative (new) mobility.")
parser.add_argument("ref_mobility", help="Name of reference mobility.")
parser.add_argument("ref_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("new_mobility", help="Name of the alternative (new) mobility.")
parser.add_argument("new_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("output_basepath", help="Output path without format suffix.")
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
# one row of plots of elvevation angles, distances and delays per overlapping period group
row_num = len(period_groups)

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
    # rows: period groups, columns: angles, distances, delays
    fig = make_subplots(rows=row_num, cols=3)   
    fig.update_layout(showlegend=False)

    #annotations identifying plot line color with respective mobility
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

        # get range of simulation seconds as list (does not include warmup time)
        start_sec = min(period_group[ref_mobility]["period"][0], period_group[new_mobility]["period"][0])
        end_sec = max(period_group[ref_mobility]["period"][1], period_group[new_mobility]["period"][1])
        sec_range = list( range(start_sec, end_sec) )
        
        # get lists of zeros to pad values of a communication period for range of the other overlapping period
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
        
        # validate paddings
        ref_vals_len = len(ref_vals_start_padding) + (period_group[ref_mobility]["period"][1] - period_group[ref_mobility]["period"][0]) + len(ref_vals_end_padding)
        new_vals_len = len(new_vals_start_padding) + (period_group[new_mobility]["period"][1] - period_group[new_mobility]["period"][0]) + len(new_vals_end_padding)
        if ref_vals_len != new_vals_len:
            raise ValueError(f"Array of reference mobility values with padding has different length than array of new mobility values with padding ({ref_vals_len} to {new_vals_len})")

        # line plots of elevation angles
        ref_angles = ref_vals_start_padding + ref_mobility_stats["angles"][ref_period_idx] + ref_vals_end_padding
        new_angles = new_vals_start_padding + new_mobility_stats["angles"][new_period_idx] + new_vals_end_padding

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=ref_angles,
                    line=dict(color='Red')),
            row=plot_row_idx, col=1,
        )
        
        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=new_angles,
                    line=dict(color='Blue')),
            row=plot_row_idx, col=1,
        )

        fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=1)
        fig.update_yaxes(title_text="elevation angle in °", row=plot_row_idx, col=1)

        # add zenith markers and shift annotation to angles plot
        ref_zenith_time = ref_mobility_stats["zenith_times"][ref_period_idx]
        new_zenith_time = new_mobility_stats["zenith_times"][new_period_idx]
        zenith_shift = new_zenith_time - ref_zenith_time

        # vertical ref. zenith line
        fig.add_shape(
            type="line",
            x0=ref_zenith_time, y0=0, x1=ref_zenith_time, y1=90,
            line=dict(color="Red", width=1, dash="dash"),
            row=plot_row_idx, col=1
        )

        # vertical new. zenith line
        fig.add_shape(
            type="line",
            x0=new_zenith_time, y0=0, x1=new_zenith_time, y1=90,
            line=dict(color="Blue", width=1, dash="dash"),
            row=plot_row_idx, col=1
        )

        # shift amount annotation
        fig.add_annotation(
            x= (new_zenith_time + ref_zenith_time) / 2 , y=-1,
            text=f"{zenith_shift} s shift",
            showarrow=False,
            font=dict(size=10, color="Blue"),
            row=plot_row_idx, col=1
        )   

        # line plots of distances
        ref_distances = ref_vals_start_padding + ref_mobility_stats["distances"][ref_period_idx] + ref_vals_end_padding
        new_distances = new_vals_start_padding + new_mobility_stats["distances"][new_period_idx] + new_vals_end_padding

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=ref_distances,
                    line=dict(color='Red')),
            row=plot_row_idx, col=2,
        )
        
        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=new_distances,
                    line=dict(color='Blue')),
            row=plot_row_idx, col=2,
        )

        fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=2)
        fig.update_yaxes(title_text="distance in km", row=plot_row_idx, col=2)

        # line plots of propagation delays
        ref_delays = ref_vals_start_padding + ref_mobility_stats["delays"][ref_period_idx] + ref_vals_end_padding
        new_delays = new_vals_start_padding + new_mobility_stats["delays"][new_period_idx] + new_vals_end_padding

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=ref_delays,
                    line=dict(color='Red')),
            row=plot_row_idx, col=3,
        )
        
        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=new_delays,
                    line=dict(color='Blue')),
            row=plot_row_idx, col=3,
        )

        fig.update_xaxes(title_text="sim. second", row=plot_row_idx, col=3)
        fig.update_yaxes(title_text="delay in ms", row=plot_row_idx, col=3)

fig.write_image(args.output_basepath + ".svg", width=1920, height=1080)
fig.write_html(args.output_basepath + ".html")