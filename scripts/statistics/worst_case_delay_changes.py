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
import json
from math import inf

# for more information on inputs and script purpose, refer to Snakefile rule worst_case_delay_change
parser = argparse.ArgumentParser()
parser.add_argument("delay_changes_csv")
parser.add_argument("communication_comparisons_dir")
parser.add_argument("tle_times")
parser.add_argument("mob2")
parser.add_argument("output_path")
args = parser.parse_args()
comm_comp_dir = args.communication_comparisons_dir if args.communication_comparisons_dir.endswith("/") else args.communication_comparisons_dir + "/"

with open(args.tle_times) as json_f:
    tle_times = json.load(json_f)

comm_comp_paths = {}
for fname in os.listdir(comm_comp_dir):
    if not args.mob2 in fname:
        continue
    modname = fname.split("_")[1]
    comm_comp_paths[modname] = comm_comp_dir + fname

forward_max_delay = 0
backward_max_delay = 0
delay_change_sum = 0
delay_change_count = 0

with open(args.delay_changes_csv, "r") as csv_f:
    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()

    for row in row_reader:
        modname = row[0]
        delay_changes = [float(change) for change in row[1:]]

        epoch_sec = int(float(tle_times["sat_times"][modname]["offset_to_start"]))

        get_max = True
        if epoch_sec < -21602 or epoch_sec > 43205 + 21602:
            get_max = False
        
        # back candidate
        is_back = False
        relevant_secs_start = None
        relevant_secs_end = None
        if epoch_sec >= 21602:
            relevant_secs_start = epoch_sec - 21602
            relevant_secs_end = epoch_sec
            is_back = True
        # forw candidate        
        elif epoch_sec < 21602:
            relevant_secs_start = epoch_sec
            relevant_secs_end = epoch_sec + 21602

        delay_change_sum = 0

        # evaluate delays in overlapping parts of availability/communication periods occuring in both compared models
        with open(comm_comp_paths[modname], "r") as json_f:
            comm_comp = json.load(json_f)


            for p in comm_comp["period_groups"]:
                
                sgp4_p = p["sgp4"]
                mob2_p = p[args.mob2]

                overlap_interval_start = max(sgp4_p["period"][0], mob2_p["period"][0])
                overlap_interval_end = min(sgp4_p["period"][1], mob2_p["period"][1], len(delay_changes))
            

                for sec in range(overlap_interval_start, overlap_interval_end):
                    if sec >= relevant_secs_start and sec <= relevant_secs_end:
                        d_change = delay_changes[sec]
                        if is_back:
                            if d_change > backward_max_delay:
                                backward_max_delay = d_change
                        else:
                            if d_change > forward_max_delay:
                                forward_max_delay = d_change
                
                    delay_change_sum += delay_changes[sec]
                    delay_change_count += 1

output_dict = {
    "max_backward_change": backward_max_delay,
    "max_forward_change": forward_max_delay,
    "average_delay": delay_change_sum / delay_change_count if delay_change_count > 0 else inf
}

with open(args.output_path, "w") as json_f:
    json.dump(output_dict, json_f)