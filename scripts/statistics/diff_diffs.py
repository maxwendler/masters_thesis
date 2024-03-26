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

import os
import csv

diff_diffs_csvs_dir = "/home/s3997128/git/ma-max-wendler/examples/space_veins/csv/pos_diff_diffs/quito"
diffs_dir = "/home/s3997128/git/ma-max-wendler/examples/space_veins/csv/pos_diff/quito"

diff_diffs_fnames = os.listdir(diff_diffs_csvs_dir)
max_diff_diff_ratio = 0
for fname in diff_diffs_fnames:
    path = diff_diffs_csvs_dir + "/" + fname
    print("diff_diff_path", path)
    constellation = fname.split("_")[0]
    const_diffs_dir = diffs_dir + "/" + constellation
    diffs_path = const_diffs_dir
    if "circular" in path:
        diffs_path = diffs_path + "/" + list(filter(lambda fname: fname.startswith("omnet") and "circular" in fname, os.listdir(const_diffs_dir)))[0]
    elif "kepler" in path:
        diffs_path = diffs_path + "/" + list(filter(lambda fname: fname.startswith("omnet") and "kepler" in fname, os.listdir(const_diffs_dir)))[0]
    else:
        raise ValueError()
    print("diffs_path", diffs_path)

    diff_diffs_dict = {}
    with open(path, "r") as diff_diffs_csv:
        row_reader = csv.reader(diff_diffs_csv)
        header = row_reader.__next__()
        for row in row_reader:
            diff_diffs_dict[row[0]] = [float(diff_diff) for diff_diff in row[1:]]

    with open(diffs_path, "r") as diffs_csv:
        row_reader = csv.reader(diffs_csv)
        header = row_reader.__next__()
        sat_counter = 0
        for row in row_reader:
            modname = row[0]
            sat_diffs = [float(diff) for diff in row[1:]]
            sat_diff_diffs = diff_diffs_dict[modname]

            for i in range(len(sat_diffs)):
                diff_diff_ratio = sat_diff_diffs[i] / sat_diffs[i]
                max_diff_diff_ratio = max(max_diff_diff_ratio, diff_diff_ratio)

            sat_counter += 1
            print(f"{sat_counter}/{len(diff_diffs_dict)} sats of {constellation}")

print("max", max_diff_diff_ratio)