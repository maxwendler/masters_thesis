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
import sys, os
from math import dist
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_dict

parser = argparse.ArgumentParser(prog="avg_sgp4_radii.py",
                                description="""Calculates average radii of satellite modules of the constellation from the specified
                                            CSV file.""")
parser.add_argument("sgp4_pos_csv", "File of Earth-centered coordinates from SGP4+TEME formatted as created by snakemake vec2csv rule.")
parser.add_argument("output_path")
args = parser.parse_args()

pos_dict, start_second, coord_field_names = parse_coords_csv_to_dict(args.sgp4_pos_csv, "teme")

avgradii_csv_lines = []
avgradii_csv_lines.append("modname,avg_radius")
for modname in pos_dict.keys():
    
    radii_sum = 0
    positions = pos_dict[modname]
    for pos in positions:
        radii_sum += dist((0, 0, 0), pos)
    avg_radius = radii_sum / len(positions)

    avgradii_csv_lines.append( modname + "," + str(avg_radius))

with open(args.output_path, "w") as out_csv:
    out_csv.write("\n".join(avgradii_csv_lines))
