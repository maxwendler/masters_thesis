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
import os

parser = argparse.ArgumentParser(prog="plot_aligned_sop_stats_at_offset.py", 
                                 description="""Plots the maximum or average elevation angle or delay difference of the aligned communication 
                                 periods of two mobilities for all satellite modules of a constellation from JSONs in the specified directory with those values, with offset to the used TLE as x values.""")
parser.add_argument("stat_diffs_or_changes_dir", help="Directory with JSONs with input data.")
parser.add_argument("new_mobility")
parser.add_argument("stat", choices=["angle", "delay"], help="Which statistic relative to SOP to plot.")
parser.add_argument("avg_or_max", choices=["avg", "max"], help="If average or maximum value of a period should be plotted.")
parser.add_argument("svg_output_path")
args = parser.parse_args()

stats_dir = args.stat_diffs_or_changes_dir if args.stat_diffs_or_changes_dir.endswith("/") else args.stat_diffs_or_changes_dir + "/"
ref_mobility = None 
new_mobility = None

# get data as (offset to epoch, zenith shift, modname) tuples
data = []
for stats_fname in filter(lambda fname: fname.endswith("aligned_differences.json") and args.new_mobility in fname, os.listdir(stats_dir)):
    
    if not ref_mobility:
        mobilties = stats_fname.split("_")[0].split("-")
        ref_mobility = mobilties[0]
        new_mobility = mobilties[1]

    stats_path = stats_dir + stats_fname
    with open(stats_path, "r") as json_f:
        stats = json.load(json_f)
    
    for p_group in stats["period_groups"]:
        data.append( tuple( [ p_group["ref_start_to_epoch_offset"], p_group[args.stat + "_differences_" + args.avg_or_max], stats["modname"] ] ))

# sort by offset to epoch
data.sort(key=lambda data_tuple: data_tuple[0])

# create point plot with modname annotation for every point
offsets = [ data_tuple[0] for data_tuple in data]
values = [data_tuple [1] for data_tuple in data]

fig = go.Figure(data=go.Scatter(x=offsets, y=values, mode='markers'))

fig.update_layout(title_text=f'{ref_mobility}-{new_mobility} {args.stat} differences relative to TLE epoch at second 0')
fig.update_xaxes(title_text='seconds to epoch')
fig.update_yaxes(title_text=f"{args.stat} 'difference' in {'°' if args.stat == 'angle' else 'ms'}")

# estimate from just trying!
average_pixel_width_per_char = 6
padding = 0
yshift_sign = 1

# modname annotations
"""
for data_tuple in data:

    modname = data_tuple[2]
    yshift = (len(modname) * average_pixel_width_per_char / 2 + padding) * yshift_sign
    yshift_sign *= -1

    fig.add_annotation(
        x=data_tuple[0], y=data_tuple[1],
        text=data_tuple[2],
        showarrow=False,
        font=dict(size=4, color="Black"),
        textangle=90,
        yshift=yshift
    )
"""

fig.write_image(args.svg_output_path, width=1920, height=1080)