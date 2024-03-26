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
import json

parser = argparse.ArgumentParser(prog="const_period_intervals",
                                 description="""Calculates intervals between the communication periods of the satellite modules
                                                of a constellation from the provided CSV, and the intervals between their
                                                zeniths from the communication period JSONs in the provided directory. 
                                                Both will be output to a CSV with from-modname,to-modname,second interval rows.""")
parser.add_argument("periods_csv")
parser.add_argument("comm_periods_dir")
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("period_intervals_outpath")
parser.add_argument("zenith_intervals_outpath")
args = parser.parse_args()

# csv header
interval_csv_lines = ["from modname|start time,to modname|end time,interval seconds"]
zenith_interval_csv_lines = ["from modname|start time,to modname|end time,interval seconds"]

# calc intervals between zeniths
comm_periods_dir = args.comm_periods_dir if args.comm_periods_dir.endswith("/") else args.comm_periods_dir + "/"
mod_comm_periods_idxs = {}

with open(args.periods_csv, "r") as periods_csv:
    row_reader = csv.reader(periods_csv)
    header = row_reader.__next__()

    # first row - interval from sim start to first period start
    try:
        first_row = row_reader.__next__()
        # first_row[1]: start of first_period
        interval_csv_lines.append("0," + first_row[0] + "," + first_row[1])
        prev_modname = first_row[0]
        prev_period_end = int(first_row[2])

        modname_periods_json_path = comm_periods_dir + prev_modname + "_communication-periods.json"

        with open(modname_periods_json_path, "r") as json_f:
            mod_periods = json.load(json_f)
        mod_zenith_time = mod_periods["zenith_times"][0]
        # first zenith was read: set idx for next read
        mod_comm_periods_idxs[prev_modname] = 1
        zenith_interval_csv_lines.append("0," + prev_modname + "," + str(mod_zenith_time))

        prev_mod_zenith_time = mod_zenith_time

        # all rows including last row -> no interval to simulation end
        for row in row_reader:
            interval_csv_lines.append( prev_modname + "," + row[0] + "," + str(int(row[1]) - prev_period_end) )
            
            modname_periods_json_path = comm_periods_dir + row[0] + "_communication-periods.json"
            
            mod_comm_period_idx = None
            if row[0] in mod_comm_periods_idxs.keys():
                mod_comm_period_idx = mod_comm_periods_idxs[row[0]]
                mod_comm_periods_idxs[row[0]] += 1
            else:
                mod_comm_period_idx = 0
                mod_comm_periods_idxs[row[0]] = 1
            
            with open(modname_periods_json_path, "r") as json_f:
                mod_periods = json.load(json_f)
            mod_zenith_time = mod_periods["zenith_times"][mod_comm_period_idx] 
            zenith_interval_csv_lines.append( prev_modname + "," + row[0] + "," +str(mod_zenith_time - prev_mod_zenith_time) )

            prev_modname = row[0]
            prev_period_end = int(row[2])
            prev_mod_zenith_time = mod_zenith_time
        
        # intervals to end
        interval_csv_lines.append( prev_modname + "," + str(args.sim_time_limit) + "," + str(args.sim_time_limit - prev_period_end) )
        zenith_interval_csv_lines.append( prev_modname + "," + str(args.sim_time_limit) + "," + str(args.sim_time_limit - prev_mod_zenith_time) )

    # no communication periods -> only write header
    except:
        pass 
    
with open(args.period_intervals_outpath, "w") as csv_out_f:
    csv_out_f.write("\n".join(interval_csv_lines))

with open(args.zenith_intervals_outpath, "w") as csv_out_f:
    csv_out_f.write("\n".join(zenith_interval_csv_lines))