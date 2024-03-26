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
import os
import plotly.express as px

parser = argparse.ArgumentParser(prog="plot_const_overlap_stats.py", description='Plots bar plot with two bars for each satellite module in the specified constellation, one for "avg_ref_coverage" and "excluded_time_to_ref_time".')
parser.add_argument("comparison_info_dir", help="Directory of the JSONs for communication comparison between two mobilities, containing a JSON for each satellite module.")
parser.add_argument("svg_output_path")
args = parser.parse_args()

modnames = []
avg_ref_coverages = []
excluded_times_to_ref_times = []

comp_info_dir = args.comparison_info_dir if args.comparison_info_dir.endswith("/") else args.comparison_info_dir + "/"
# get sorted lists of communication period JSON paths
info_json_paths = sorted( [ comp_info_dir + fname for fname in list( filter( lambda fname: fname.endswith("_communication_comparison.json"), os.listdir(comp_info_dir) ) ) ] ) 

# load values from JSONs
for path in info_json_paths:
    with open(path, "r") as json_f:
        comm_periods = json.load(json_f)
        modnames.append(comm_periods["modname"])
        avg_ref_coverages.append( comm_periods["avg_ref_coverage"] )
        excluded_times_to_ref_times.append( comm_periods["total_excluded_time_to_ref_time"] )

# prepare x-axis modnames, each name two times for two-bar bar groups
modnames_list = []
for modname in modnames:
    modnames_list += [modname] * 2
# prepare value and category for each bar
vals_list = []
categories_list = []
for i in range(0, len(avg_ref_coverages)):
    vals_list.append(avg_ref_coverages[i])
    vals_list.append(excluded_times_to_ref_times[i])
    categories_list.append("avg_ref_coverage")
    categories_list.append("excluded_time_to_ref_time")

fig = px.histogram(x=modnames_list, y=vals_list, color=categories_list, barmode='group', histfunc=None)
fig.update_yaxes(title_text="%")
fig.write_image(args.svg_output_path)
fig.write_html(args.svg_output_path.removesuffix("svg") + "html")