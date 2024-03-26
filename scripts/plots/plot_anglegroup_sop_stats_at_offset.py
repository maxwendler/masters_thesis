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
from numpy.polynomial import Polynomial

# refer to Snakefile rule plot_anglegroup_aligned_delay_duration_diffs_at_offset for more information on inputs and script purpose
parser = argparse.ArgumentParser(prog="plot_anglegroup_aligned_sop_stat_at_offset")
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

average_pixel_width_per_char = 0.005

# create a plot for each angle interval group
for interval_factor_str in grouped_periods.keys():
    
    interval_factor = int(interval_factor_str)
    interval_start_angle = interval_factor * args.angle_interval
    interval_end_angle = (interval_factor + 1) * args.angle_interval

    periods = grouped_periods[interval_factor_str]
    if len(periods) == 0:
        continue

    offsets_to_epoch = []
    avg_delay_diffs = []
    max_delay_diffs = []
    duration_diffs = []
    modnames = []

    for p in periods:
        modnames.append(p["modname"])
        offsets_to_epoch.append(p["period_group"]["ref_start_to_epoch_offset"])
        delay_diffs = p["period_group"]["delay_differences"]
        max_delay_diffs.append(max(delay_diffs))
        avg_delay_diffs.append(sum(delay_diffs) / len(delay_diffs))
        
        ref_duration = p["period_group"]["sgp4"]["period"][1] - p["period_group"]["sgp4"]["period"][0]
        new_duration = p["period_group"][args.new_mobility]["period"][1] - p["period_group"][args.new_mobility]["period"][0]
        duration_diffs.append(abs(ref_duration - new_duration))

    # delay difference figure
    fig = go.Figure(data=go.Scatter(x=offsets_to_epoch, y=avg_delay_diffs, name="avg. delay difference", mode='markers'))
    fig.add_trace(go.Scatter(x=offsets_to_epoch, y=max_delay_diffs, name="max. delay difference", mode='markers'))
    
    positive_offsets_to_epoch = []
    positive_offset_max_delay_diffs = []
    for offset_idx in range(len(offsets_to_epoch)):
        offset_to_epoch = offsets_to_epoch[offset_idx]
        max_delay_diff = max_delay_diffs[offset_idx]
        if offset_to_epoch >= 0:
            positive_offsets_to_epoch.append(offset_to_epoch)
            positive_offset_max_delay_diffs.append(max_delay_diff)

    # line fit of forward propagation delay at offset to epoch function
    if len(positive_offsets_to_epoch) > 1:
        positive_offset_linear_fun = Polynomial.fit(positive_offsets_to_epoch, positive_offset_max_delay_diffs, deg=1)
        linear_fun_xs = [0, max(offsets_to_epoch)]
        linear_fun_ys = [positive_offset_linear_fun(0), positive_offset_linear_fun(linear_fun_xs[1])]
        fig.add_trace(go.Scatter(x=linear_fun_xs, y=linear_fun_ys, mode='lines', name="max. delay difference function", line=dict(color="red")))

        fig.update_layout(title_text=f"y={str(positive_offset_linear_fun.convert())}")

    # modname annotations
    """
    for modname_idx in range(len(modnames)):
        modname = modnames[modname_idx]
        offset_to_epoch = offsets_to_epoch[modname_idx]
        y_shift = (len(modname) * average_pixel_width_per_char / 2)

        fig.add_annotation(
            dict(
                font=dict(color="black",size=5),
                x=offset_to_epoch,
                y=-y_shift,
                text=modname,
                textangle=90,
                showarrow=False
            )
        )
    """

    fig_path = delay_diffs_output_dir + str(interval_start_angle) + "_to_" + str(interval_end_angle) + "_deg_delay_differences.svg"
    fig.write_image(fig_path)

    # duration difference figure
    fig = go.Figure(data=go.Scatter(x=offsets_to_epoch, y=duration_diffs, name="duration difference", mode='markers'))

    # modname annotations
    """
    for modname_idx in range(len(modnames)):
        modname = modnames[modname_idx]
        offset_to_epoch = offsets_to_epoch[modname_idx]
        y_shift = (len(modname) * average_pixel_width_per_char / 2)

        fig.add_annotation(
            dict(
                font=dict(color="black",size=5),
                x=offset_to_epoch,
                y=-y_shift,
                text=modname,
                textangle=90,
                showarrow=False
            )
        )
    """
        
    fig_path = duration_diffs_output_dir + str(interval_start_angle) + "_to_" + str(interval_end_angle) + "_deg_duration_differences.svg"
    fig.write_image(fig_path)