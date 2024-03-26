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
from scripts.statistics.positional_differences import parse_coords_csv_to_dict
from math import dist, acos
import astropy.units as u
from astropy.coordinates import Angle

parser = argparse.ArgumentParser(prog="sop_stats.py",description="Calulcates satellite elevation angle, satelitte distance to SOP, and propagation delay from given omnetCoord csv.")
parser.add_argument("csv_path")
parser.add_argument("sop_coord", nargs=3, type=float)
parser.add_argument("output_dir")
parser.add_argument("-e", "--eval_angle", type=float, help="Only calculate propgation delay when communication is possible with given minimum elevation angle (float). Entry is 0 otherwise.")
args = parser.parse_args()
output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"
output_base_fname = args.csv_path.split("/")[-1].removesuffix("_omnet_sorted.csv")

# load coordinates from csv
sat_coord_dict, start_second, _coord_field_names = parse_coords_csv_to_dict(args.csv_path, frame="omnet")
min_eval_angle = args.eval_angle
sop_coord = args.sop_coord

# create header for all values of a module in a row
header = "modname"
for i in range(start_second, start_second + len(list(sat_coord_dict.values())[0])):
    header += "," + str(i)

distances_path = output_dir + output_base_fname + "_distances.csv"
distance_f = open(distances_path, "w")
distance_f.write(header + "\n")

angles_path = output_dir + output_base_fname + "_angles.csv"
elev_angles_f = open(angles_path, "w")
elev_angles_f.write(header + "\n")

propagation_delay_path = output_dir + output_base_fname + "_delays.csv"
prop_delay_f = open(propagation_delay_path, "w")
prop_delay_f.write(header + "\n")

distance_csv_lines = [header]
elev_angles_csv_lines = [header]
propagation_delay_csv_lines = [header]

# calculate elevation angles, distances and delays to SOP 
sat_counter = 0
for satname in sat_coord_dict.keys():
    
    sop_sat_distances = [] 
    sop_sat_elev_angles = []
    sat_propagation_delays = []
    for i in range(0, len(sat_coord_dict[satname]) ):
        
        sat_coord = sat_coord_dict[satname][i]

        # calc distance
        distance = dist(sop_coord, sat_coord)
        sop_sat_distances.append( distance )

        # calc angle to omnet x(east)y(north) plane
        # up coord is 0
        vec_in_plane = ( sat_coord[0] - sop_coord[0], sat_coord[1] - sop_coord[1], 0 )
        dot_product = sat_coord[0] * vec_in_plane[0] + sat_coord[1] * vec_in_plane[1] + sat_coord[2] * vec_in_plane[2]
        cos_val = (dot_product) / (dist(vec_in_plane, sop_coord) * dist(sat_coord, sop_coord))
        # floating point calculation can lead to values surpassing one, which are not compatible with acos
        if cos_val > 1:
            cos_val = 1
        angle_to_plane_rad = Angle(acos( cos_val ), u.rad)
        angle_to_plane_deg = angle_to_plane_rad.degree

        # if 'up' coordinate is negative, angle will be negative
        elev_angle = angle_to_plane_deg
        if sat_coord[2] < 0:
            elev_angle *= -1
        sop_sat_elev_angles.append( elev_angle )

        delay = 0
        if elev_angle > min_eval_angle or not args.eval_angle:
            # *.radioMedium.propagation.propagationSpeed = 299792458 mps # speed of light
            # * 1000 -> ms
            delay = distance * 1000 / 299792.458
        sat_propagation_delays.append(delay)

    # create rows for new CSVs
    new_line = satname
    for d in sop_sat_distances:
        new_line += "," + str(d)
    distance_f.write(new_line + "\n")

    new_line = satname
    for a in sop_sat_elev_angles:
        new_line += "," + str(a)
    elev_angles_f.write(new_line + "\n")

    new_line = satname
    for d in sat_propagation_delays:
        new_line += "," + str(d)
    prop_delay_f.write(new_line + "\n")

    sat_counter += 1
    print(args.csv_path.split("/")[-1] + ": " + f"{sat_counter}/{len(sat_coord_dict)}")

distance_f.close()
elev_angles_f.close()
prop_delay_f.close()