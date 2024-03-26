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

parser = argparse.ArgumentParser(prog="available_sats_at_simtime.py",
                                 description="""Calculates absolute times and ratios of these times w.r.t. total simulation time of availability
                                                of (1) specific numbers of available satellites, and (2) availability of >=1, >=2, >=3 satellites,
                                                for specified location, constellation and mobility model.
                                                """)
parser.add_argument("comm_period_jsons_dir", help="directory of communication periods of mobility w.r.t. a certain location")
parser.add_argument("mobility")
parser.add_argument("measurement_start_time", type=int)
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("ouput_path")
args = parser.parse_args()

comm_periods_jsons_dir = args.comm_period_jsons_dir if args.comm_period_jsons_dir.endswith("/") else args.comm_period_jsons_dir + "/"

# load communication period information
comm_period_dicts = []
for comm_period_json_fname in os.listdir(comm_periods_jsons_dir):
    
    if args.mobility not in comm_period_json_fname:
        continue

    comm_periods_path = comm_periods_jsons_dir + comm_period_json_fname
    with open(comm_periods_path, "r") as json_f:
        sat_comm_periods = json.load(json_f)
    
    modname = sat_comm_periods["modname"]
    for period in sat_comm_periods["periods"]:
        comm_period_dicts.append({"modname": modname, "period": period})

available_sats = []
availability_num_times = {}

# count availabilities of each satellite number
for sim_time in range(args.measurement_start_time, args.sim_time_limit + 1):
    
    current_available_sats = []
    for comm_period_dict in comm_period_dicts:
        period = comm_period_dict["period"]
        if period[0] <= sim_time and sim_time <= period[1]:
            current_available_sats.append(comm_period_dict["modname"])
    
    sat_num = len(current_available_sats)
    if sat_num in availability_num_times.keys():
        availability_num_times[sat_num] += 1
    else:
        availability_num_times[sat_num] = 1

    available_sats.append({
        "sim_time": sim_time,
        "sat_num": len(current_available_sats),
        "sats": current_available_sats
    })

# calculate ">=X availabilites"
at_least_one_available_time = 0
at_least_two_available_time = 0
at_least_three_available_time = 0
for sat_num in availability_num_times.keys():
    if sat_num > 0:
        at_least_one_available_time += availability_num_times[sat_num]
        if sat_num > 1:
            at_least_two_available_time += availability_num_times[sat_num]
            if sat_num > 2:
                at_least_three_available_time += availability_num_times[sat_num]

# calculate availability time ratios to total time
availability_num_ratios = {}
for availability_num_time in availability_num_times.items():
    availability_num_ratios[availability_num_time[0]] = availability_num_time[1] / args.sim_time_limit
at_least_one_available_ratio = at_least_one_available_time / args.sim_time_limit
at_least_two_available_ratio = at_least_two_available_time / args.sim_time_limit
at_least_three_available_ratio = at_least_three_available_time / args.sim_time_limit

output = {
    "availability_num_times": availability_num_times,
    "at_least_one_time": at_least_one_available_time,
    "availability_num_ratios": availability_num_ratios,
    "at_least_one_ratio": at_least_one_available_ratio,
    "at_least_two_ratio": at_least_two_available_ratio,
    "at_least_three_ratio": at_least_three_available_ratio,
    "available_sats": available_sats
}

with open(args.ouput_path, "w") as out_json:
    json.dump(output, out_json, indent=4)