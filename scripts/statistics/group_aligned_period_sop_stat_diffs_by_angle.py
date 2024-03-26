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
import os
import json
from math import floor

# refer to Snakefile rule group_const_aligned_local_sop_stat_diffs for more details on inputs.
parser = argparse.ArgumentParser(prog="group_aligned_period_sop_stat_diffs_by_angle.py")
parser.add_argument("ref_comm_period_jsons_dir")
parser.add_argument("aligned_stat_diffs_dir")
parser.add_argument("new_mobility")
parser.add_argument("angle_interval", type=int)
parser.add_argument("output_path")
args = parser.parse_args()

ref_comm_period_jsons_dir = args.ref_comm_period_jsons_dir if args.ref_comm_period_jsons_dir.endswith("/") else args.ref_comm_period_jsons_dir + "/"
aligned_stat_diffs_dir = args.aligned_stat_diffs_dir if args.aligned_stat_diffs_dir.endswith("/") else args.aligned_stat_diffs_dir + "/"

# groups of (modname,period_idx) pairs
# grouping of communication periods by maximum occuring elevation angle
grouped_periods = {}
for comm_period_json_fname in os.listdir(ref_comm_period_jsons_dir):
    
    json_path = ref_comm_period_jsons_dir + comm_period_json_fname
    with open(json_path, "r") as json_f:
        mod_comm_periods = json.load(json_f)
    
    modname = mod_comm_periods["modname"]

    for period_idx in range(len(mod_comm_periods["angles"])):
        angle_vals = mod_comm_periods["angles"][period_idx]
        max_angle = max(angle_vals)
        group = floor( max_angle / args.angle_interval )
        if group not in grouped_periods.keys():
            grouped_periods[group] = [ {"modname": modname, "period_idx": period_idx} ]
        else:
            grouped_periods[group].append( {"modname": modname, "period_idx": period_idx} )

# assign differences of desired stat to grouped periods
for aligned_stat_diffs_fname in filter(lambda fname: fname.endswith("aligned_differences.json") and args.new_mobility in fname, os.listdir(aligned_stat_diffs_dir)):

    json_path = aligned_stat_diffs_dir + aligned_stat_diffs_fname
    with open(json_path, "r") as json_f:
        mod_aligned_stat_diffs = json.load(json_f)
    
    modname = mod_aligned_stat_diffs["modname"]

    # add period group to period in grouped periods
    for period_idx in range(len(mod_aligned_stat_diffs["period_groups"])):
        period_group = mod_aligned_stat_diffs["period_groups"][period_idx]
        
        # might be in any group, break if forund
        for group in grouped_periods.keys():
            group_periods = grouped_periods[group]
            period_found = False
            # might be any period of group, break if found
            for period in group_periods:
                if period["modname"] == modname and period["period_idx"] == period_idx:
                    period["period_group"] = period_group
                    period_found = True
                    break
            if period_found:
                break

# remove periods that have no period group, i.e. lost or new periods
for group in grouped_periods.keys():
    
    group_periods = grouped_periods[group]
    
    to_be_removed_idxs = []
    for group_period_idx in range(len(group_periods)):
        period = group_periods[group_period_idx]
        if "period_group" not in period.keys():
            to_be_removed_idxs.append(group_period_idx)
    
    to_be_removed_idxs.reverse()
    for group_period_idx in to_be_removed_idxs:
        group_periods.pop(group_period_idx)
    grouped_periods[group] = group_periods

with open(args.output_path, "w") as out_json:
    json.dump(grouped_periods, out_json, indent=4)