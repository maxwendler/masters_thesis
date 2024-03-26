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
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_aligned_sop_stats_at_offset.py", 
                                 description="""Plots the maximum or average elevation angle or delay change or difference of the aligned communication 
                                 periods of two mobilities for a satellite module from a JSON with those values, with offset to the used TLE as x values.""")
parser.add_argument("stat_diffs_or_changes_json", help="JSON with input data.")
parser.add_argument("stat", choices=["angle", "delay"], help="Which statistic relative to SOP to plot.")
parser.add_argument("avg_or_max", choices=["avg", "max"], help="If average or maximum value of a period should be plotted.")
parser.add_argument("svg_output_path")

args = parser.parse_args()
use_changes = "changes" in args.stat_diffs_or_changes_json

with open(args.stat_diffs_or_changes_json, "r") as json_f:
    input_data = json.load(json_f)

mobilties = args.stat_diffs_or_changes_json.split("/")[-1].split("_")[0].split("-")
ref_mobility = mobilties[0]
new_mobility = mobilties[1]

offsets = []
values = []

for period_group in input_data["period_groups"]:
    offsets.append(period_group["ref_start_to_epoch_offset"])
    if use_changes:
        values.append(period_group[ args.stat + "_changes_" + args.avg_or_max ])
    else:
        values.append(period_group[ args.stat + "_differences_" + args.avg_or_max ])
    

fig = go.Figure(data=go.Scatter(x=offsets, y=values, mode='lines+markers'))

fig.update_layout(title_text=f'{ref_mobility}-{new_mobility} {args.stat} {"changes" if use_changes else "differences"} {args.avg_or_max} relative to TLE epoch at second 0')
fig.update_xaxes(title_text='seconds to epoch')
fig.update_yaxes(title_text=f"{args.stat} {'change' if use_changes else 'difference'} in {'°' if args.stat == 'angle' else 'ms'}")

fig.write_image(args.svg_output_path)