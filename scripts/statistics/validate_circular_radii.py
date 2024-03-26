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
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_dict
from math import dist

# Has no according Snakefile rule anymore.
parser = argparse.ArgumentParser(description="Outputs radii of orbits in given csv. Intended for validating how circular the circular model's actually are.")
parser.add_argument("teme_coords_csv")
parser.add_argument("output_path")
args = parser.parse_args()

coords_teme_dict, start_second, coord_field_names = parse_coords_csv_to_dict(args.teme_coords_csv, "teme")

result_lines = []

for modname in coords_teme_dict.keys():
    coords = coords_teme_dict[modname]
    radius = None
    radii = []
    is_circle = True
    for c in coords:
        
        current_radius = dist( [0,0,0], c )
        radii.append(current_radius)

        if not radius:
            radius = current_radius
        else:
            if radius != current_radius:
                is_circle = False
    
    if not is_circle:
        result_lines.append( f"{modname}, invalid, {radii}" )
    else:
        result_lines.append( f"{modname}, valid, {radii}")

os.makedirs( "/".join(args.output_path.split("/")[:-1]) , exist_ok=True)

with open(args.output_path, "w") as out_f:
    out_f.write("\n".join(result_lines))