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

parser = argparse.ArgumentParser(prog="all_const_periods.py",
                                 description="""Creates CSV with ordered communication periods with the SOP of satellite constellation,
                                                satellite module name, period start, period end in each row; order by period start.""")
parser.add_argument("period_jsons_dir", help="Directory with the communication period JSONs of a constellation.")
parser.add_argument("output_path")
args = parser.parse_args()

period_jsons_dir = args.period_jsons_dir if args.period_jsons_dir.endswith("/") else args.period_jsons_dir + "/"

# modname, period start, period end
data_tuples = []
for comm_period_json_fname in os.listdir(period_jsons_dir):
    
    json_path = period_jsons_dir + comm_period_json_fname
    with open(json_path, "r") as json_f:
        comm_periods = json.load(json_f)
    
    period_idx = 0
    for period in comm_periods["periods"]:
        data_tuples.append( tuple( [comm_periods["modname"], period[0], period[1], period_idx] ) )
        period_idx += 1

data_tuples.sort(key=lambda d_tuple: d_tuple[1])

# header
csv_lines = [ "satellite module,period start second,period end second,period index" ]
for d_tuple in data_tuples:
    csv_lines.append(",".join( [ str(tuple_item) for tuple_item in d_tuple] ))

os.makedirs("/".join(args.output_path.split("/")[:-1]), exist_ok=True)

with open(args.output_path, "w") as csv_f:
    csv_f.write("\n".join(csv_lines))