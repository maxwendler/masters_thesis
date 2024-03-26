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
import csv
import os

parser = argparse.ArgumentParser(prog="omnet_stat_differences.py", description="Calculates difference or change in elevation angle / distance / delay for SOP stat csvs of two different mobilities.")
parser.add_argument("ref_mobility_csv_path")
parser.add_argument("new_mobility_csv_path")
parser.add_argument("output_path")
parser.add_argument("-c", "--change", action="store_true", help="Calculates decrease/increase instead of difference magnitude.")
args = parser.parse_args()

ref_stats = {}
ref_column_num = 0
new_header = ""

# parse values from CSVs
with open(args.ref_mobility_csv_path, "r") as stat_f:
    row_reader = csv.reader(stat_f)
    header = row_reader.__next__()
    ref_column_num = len(header)
    new_header = ",".join(header)

    for row in row_reader:
        modname = row[0]
        stat_vals = [float(v) for v in row[1:]]
        ref_stats[modname] = stat_vals

new_stats = {}
with open(args.new_mobility_csv_path, "r") as stat_f:
    row_reader = csv.reader(stat_f)
    header = row_reader.__next__()
    if len(header) != ref_column_num:
        raise AssertionError(f"CSV of ref_mobility has {ref_column_num} entries, while second CSV has {len(header)}!")

    for row in row_reader:
        modname = row[0]
        stat_vals = [float(v) for v in row[1:]]
        new_stats[modname] = stat_vals

new_csv_lines = [new_header]

# calculate differences or changes
for modname in ref_stats.keys():
    
    stat_diffs_or_changes = []
    for i in range(0, len(ref_stats[modname])):
        
        ref_val = ref_stats[modname][i]
        new_val = new_stats[modname][i]

        if args.change:
            stat_diffs_or_changes.append( new_val -  ref_val )        
        else:
            stat_diffs_or_changes.append( abs(new_val - ref_val) )
    
    new_line = modname
    for val in stat_diffs_or_changes:
        new_line += "," + str(val)
    new_csv_lines.append(new_line)

out_dir = "/".join(args.output_path.split("/")[:-1])
os.makedirs(out_dir, exist_ok=True)

output = "\n".join(new_csv_lines)
with open(args.output_path, "w") as out_f:
    out_f.write(output)