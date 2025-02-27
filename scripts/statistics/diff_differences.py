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

def parse_diff_csv(csv_path, eval_coord_dims):
    """
    Parses CSV with positional differences per module in each line to modname-difference list dictionary. 
    """
    with open(csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()

        diffs = {}
        for row in row_reader:
            row_stat_name = row[0]
            if "_vector" in row_stat_name:
                if eval_coord_dims:
                    diffs[row_stat_name] = [float(d) for d in row[1:]]
            else:
                diffs[row_stat_name] = [float(d) for d in row[1:]]
        
        return diffs

parser = argparse.ArgumentParser(prog="calc_diff_difference", description="Calculates the difference in difference values from two csvs with one list of differences per line, i.e. produces one list of differences of differences per line via print()")
parser.add_argument("csv_path1")
parser.add_argument("csv_path2")
parser.add_argument("-c", "--coord_dims", action="store_true", help="If flag is set, distances in individual coordinate dimensions will be output, if according lines exist.")
args = parser.parse_args()

csv_path1 = args.csv_path1
csv_path2 = args.csv_path2
eval_coord_dims = args.coord_dims

diffs1 = parse_diff_csv(csv_path1, eval_coord_dims)
diffs2 = parse_diff_csv(csv_path2, eval_coord_dims)

test_key = list(diffs1.keys())[0]
if len( diffs1[test_key] ) != len( diffs2[test_key] ):
    raise ValueError(f"{csv_path1} has more difference values per statistic ({len(diffs1[test_key])}) than {csv_path2} ({len(diffs2[test_key])})!")

# calculate differences for each satellite module
sorted_stat_names = sorted(diffs1.keys())
diff_diffs_lines = []
for stat_name in sorted_stat_names:
    new_line = stat_name
    for i in range(0, len(diffs1[stat_name])):
        diffs_d = abs(diffs1[stat_name][i] - diffs2[stat_name][i])
        new_line += "," + str(diffs_d)
    diff_diffs_lines.append(new_line)

# copy header from one of the csvs
header = ""
with open(csv_path1, "r") as csv_f:
    header = csv_f.readline().removesuffix("\n")
diff_diffs_lines = [header] + diff_diffs_lines

output = "\n".join(diff_diffs_lines)
print(output)