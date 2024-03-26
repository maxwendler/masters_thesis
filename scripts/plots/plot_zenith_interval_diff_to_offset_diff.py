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
from numpy.polynomial import Polynomial

# for info on script inputs and purpose, refer to Snakefile rules plot_sat_comm_period_zenith_interval_changes
# and plot_const_comm_period_zenith_interval_changes_at_offset_diff
parser = argparse.ArgumentParser(prog="plot_zenith_interval_diff_at_offset_diff")
parser.add_argument("all_mod_interval_changes_json")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.all_mod_interval_changes_json, "r") as json_f:
    all_mod_interval_changes = json.load(json_f)

# gather between-model differences of communication period zenith intervals and according offset differences
abs_interval_differences = []
abs_offset_differences = []
for sat_relation_changes in all_mod_interval_changes["same_periods_changes"].values():
    
    for overlap_relation in sat_relation_changes["overlap_changes"]:
        abs_interval_differences.append(abs(overlap_relation["zenith_interval_difference"]))
        abs_offset_differences.append(overlap_relation["abs_offset_difference"])
    
    abs_interval_differences.append(abs(sat_relation_changes["next_nonoverlap_changes"]["zenith_interval_difference"]))
    abs_offset_differences.append(sat_relation_changes["next_nonoverlap_changes"]["abs_offset_difference"])

if len(abs_interval_differences) == 0:    
    fig = go.Figure()
    fig.add_annotation(dict(font=dict(color="black",size=40),
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    text="No common communication for which intervals exist.",
                    textangle=0,
                    xref="paper",
                    yref="paper"))
    
else:

    if len(abs_interval_differences) > 1:
        # fitting of linear function
        # fit linear function including outliers
        all_vals_fun = Polynomial.fit(abs_offset_differences, abs_interval_differences, deg=1)

        # remove fixed num of outliers
        predictions = [all_vals_fun(x) for x in abs_offset_differences]
        errors = []
        for i in range(len(abs_interval_differences)):
            diff = abs_interval_differences[i]
            prediction = predictions[i]
            errors.append(abs(diff - prediction))

        # use max x from before removal of outliers
        inliers_fun_xs = [0, max(abs_offset_differences)]

        # find 0 most outlying points
        outlier_xs = []
        outlier_ys = []
        for i in range(0):
            outlier_idx = errors.index(max(errors))
            errors.pop(outlier_idx)
            outlier_xs.append(abs_offset_differences.pop(outlier_idx))
            outlier_ys.append(abs_interval_differences.pop(outlier_idx))

        print("outliers:")
        print(outlier_xs)
        print(outlier_ys)

        # fit new linear function ignoring the outliers
        inliers_fun = Polynomial.fit(abs_offset_differences, abs_interval_differences, deg=1)
        inliers_fun_ys = [inliers_fun(0), inliers_fun(inliers_fun_xs[1])]

    fig = go.Figure(data=go.Scatter(x=abs_offset_differences, y=abs_interval_differences, mode='markers',line=dict(color="blue")))
    fig.update_xaxes(title_text='absolute seconds difference in offset to epoch')
    
    if len(abs_interval_differences) > 1:
        fig.update_layout(title=f"y={str(inliers_fun.convert())}")
        fig.add_trace(go.Scatter(x=outlier_xs, y=outlier_ys, mode='markers', line=dict(color="red")))
        fig.add_trace(go.Scatter(x=inliers_fun_xs, y=inliers_fun_ys, mode='lines', line=dict(color="blue", dash="dash")))

    fig.update_yaxes(title_text='absolute interval difference in seconds')
    
fig.write_image(args.output_path)