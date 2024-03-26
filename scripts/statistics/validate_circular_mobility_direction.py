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
import numpy as np

# Has no according Snakefile rule anymore.
parser = argparse.ArgumentParser()
parser.add_argument("sgp4_teme_positions_csv")
parser.add_argument("circular_teme_positions_csv")
args = parser.parse_args()

sgp4_teme_dict, start_second, coord_field_names = parse_coords_csv_to_dict(args.sgp4_teme_positions_csv, "teme")
circular_teme_dict, start_second, coord_field_names = parse_coords_csv_to_dict(args.circular_teme_positions_csv, "teme")

# for each satellite module: 
# check if circular direction roughly aligns via perpendicular vector from cross product
# as circular planes from different models are sligthly different, "aligned" direction is defined as:
# angle between perpendicular vectors < 90 °; 
# if circle is e.g. clockwise instead of counterclockwise, perpendicular vector would be on other side 
# of circle plane, with angle between perpendicular vectors of both models > 90 deg
result_strs = []
for modname in sgp4_teme_dict.keys():
    
    # for calculating perpendicular vector with cross product, use position vector at sim start second and 1 minute later
    # for both models
    sgp4_start_sec_pos = sgp4_teme_dict[modname][0]
    sgp4_60_sec_pos = sgp4_teme_dict[modname][60]
    sgp4_perpendicular = np.cross(sgp4_start_sec_pos, sgp4_60_sec_pos)

    circular_start_sec_pos = circular_teme_dict[modname][0]
    circular_60_sec_pos = circular_teme_dict[modname][60]
    circular_perpendicular = np.cross(circular_start_sec_pos, circular_60_sec_pos)

    # angle calculation derived from https://en.wikipedia.org/wiki/Dot_product#Geometric_definition
    angle = np.arccos(np.dot(sgp4_perpendicular, circular_perpendicular) / (np.linalg.norm(sgp4_perpendicular) * np.linalg.norm(circular_perpendicular)))
    degrees = np.degrees(angle)

    result = modname + ": "
    if degrees < 90:
        result += "valid, "
    else:
        result += "invalid, "
    result += str(degrees) + "°"
    result_strs.append(result)

print("\n".join(result_strs))