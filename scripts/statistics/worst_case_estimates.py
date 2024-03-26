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
import csv

parser = argparse.ArgumentParser()
parser.add_argument("pos_diff_csv")
parser.add_argument("tle_times")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.tle_times, "r") as times_json:
    tle_times = json.load(times_json)

satnum = len(tle_times["sat_times"])

# only consider periods of roughly 6 hours of backward/forward propagatio
# as shows below, not existance of this time in both directions is required; 
# as it is half of the time, only one direction per module will be evaluated
fit_period_len_limit = int(43205 * 4 / 8)

# get mod pos_diffs
output_dict = {}
before_max_diff = 0
before_max_modnames_list = []
after_max_diff = 0
after_max_modnames_list = []

sat_counter = 0
diff_csv_fname = args.pos_diff_csv.split("/")[-1]

with open(args.pos_diff_csv, "r") as diff_csv:
    row_reader = csv.reader(diff_csv)
    header = row_reader.__next__()

    for row in row_reader:
        mod_dict = {}
        modname = row[0]
        mod_diffs = [float(diff) for diff in row[1:]]
        epoch_sec = int(float(tle_times["sat_times"][modname]["offset_to_start"])) 

        mod_secs_after_epoch = 0
        mod_secs_before_epoch = 0

        if epoch_sec > 0:
            if epoch_sec < 43205:
                mod_secs_before_epoch = epoch_sec
            else:
                mod_secs_before_epoch = 43205
            mod_secs_after_epoch = 43205 - mod_secs_before_epoch
        else:
            mod_secs_before_epoch = 0
            mod_secs_after_epoch = 43205

        # backward max
        # second part of condition ensures that epoch is actually touched
        if mod_secs_before_epoch >= fit_period_len_limit and mod_secs_before_epoch < 43205:
            before_diffs = list(reversed(mod_diffs[:(mod_secs_before_epoch+1)]))[:fit_period_len_limit + 1]
            max_diff = max(before_diffs)
            if max_diff > before_max_diff:
                before_max_modnames_list.insert(0, modname)
                before_max_diff = max_diff

        # forward max
        # second part of condition ensures that epoch is actually touched
        if mod_secs_after_epoch >= fit_period_len_limit and mod_secs_after_epoch < 43205:
            
            diff_idx_offset = 0
            if epoch_sec >= 0:
                diff_idx_offset = epoch_sec
            else:
                diff_idx_offset = 0

            after_diffs = mod_diffs[diff_idx_offset:(diff_idx_offset + mod_secs_after_epoch+1)][:fit_period_len_limit + 1]
            max_diff = max(after_diffs)
            if max_diff > after_max_diff:
                after_max_diff = max_diff
                after_max_modnames_list.insert(0, modname)
        
        sat_counter += 1 
        print(f"{diff_csv_fname}: {sat_counter}/{satnum}")

output_dict["before_max_diff"] = before_max_diff
output_dict["before_max_modname"] = before_max_modnames_list
output_dict["after_max_diff"] = after_max_diff
output_dict["after_max_modnames"] = after_max_modnames_list

with open(args.output_path, "w") as out_f:
    json.dump(output_dict, out_f, indent=4)
