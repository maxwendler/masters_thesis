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

import csv
import re

def parse_coords_csv_to_list(csv_path: str) -> tuple[list[tuple[float, float, float], int]]:
    """
    Parses coordinates OMNeT++ results CSV only containing one type of coordinates obtained from lib/veins_scripts/eval/opp_vec2csv.pl script 
    to list of 3D coordinates. Also returns the start second of the simulation.  
    """
    coords = []
    with open(csv_path, "r") as csv_f:
        
        row_reader = csv.reader(csv_f, delimiter="\t")
        
        # find indexes of coordinate fields 
        header = row_reader.__next__()
        coord_field_idxs = []
        for field in range(0, len(header)):
            if "Coord" in header[field]:
                coord_field_idxs.append(field)
        if len(coord_field_idxs) > 3:
            raise AssertionError("No 3D coordinates - found more than three coordinate fields in this CSV.")

        # read 3D coords and start second
        start_second = None
        for row in row_reader:
            if not start_second:
                start_second = int(row[1])
            row_coords = []
            for i in coord_field_idxs:
                row_coords.append(float(row[i]))
            coords.append( tuple(row_coords) )
    
    return coords, start_second

def sort_wgs84_coord_fieldnames(fieldnames: list[str]) -> list[str]:
    """
    Sorts coordinate field names of coordinate csv in ordner Lat, Lon, Alt
    """    
    coord_field_names_sorted = []
    coord_field_names_sorted.append(filter(lambda col_name: "CoordLat" in col_name, fieldnames).__next__())
    coord_field_names_sorted.append(filter(lambda col_name: "CoordLon" in col_name, fieldnames).__next__())
    coord_field_names_sorted.append(filter(lambda col_name: "CoordAlt" in col_name, fieldnames).__next__())
    return coord_field_names_sorted

modname_re = r"leo.*]"

def parse_coords_csv_to_dict(csv_path: str, frame: str) -> tuple[dict[str, list[tuple[float, float, float]]], int, list[str]]:
    """
    Parses 3D coordinate csv with one coordinate of a satellite module per row into a module_name:coordinates_list dict. 
    """
    coord_dict = {}
    coord_field_names = None
    with open(csv_path, "r") as csv_f:
        first_row_reader = csv.DictReader(csv_f, delimiter="\t")
        first_row = first_row_reader.__next__()
        
        # in same order as in header
        coord_field_names = list(filter(lambda col_name: col_name.endswith("_vector"), first_row.keys()))
        # needs reordering for wgs84
        if frame == "wgs84":
            coord_field_names = sort_wgs84_coord_fieldnames(coord_field_names)
        start_second = int(first_row["time"])

        csv_f.seek(0)

        reader = csv.DictReader(csv_f, delimiter="\t")
        current_mod = ""
        current_mod_3d_coords = []

        for row in reader:
            if row["node"] == current_mod:
                current_mod_3d_coords.append( (float(row[coord_field_names[0]]), 
                                                float(row[coord_field_names[1]]), 
                                                float(row[coord_field_names[2]]) ) )
            
            else:
                if current_mod != "":
                    # save coords of mod
                    coord_dict[current_leo_modname] = current_mod_3d_coords

                # setup new current_mod with coords from current line
                current_mod = row["node"]
                current_leo_modname = re.search(modname_re, row["node"]).group()
                current_mod_3d_coords = {}
                current_mod_3d_coords = [   (float(row[coord_field_names[0]]), 
                                            float(row[coord_field_names[1]]), 
                                            float(row[coord_field_names[2]]) ) ]
        
        # save results to dict after last row
        coord_dict[current_leo_modname] = current_mod_3d_coords

    return coord_dict, start_second, coord_field_names

def get_mod_row(csv_path, modname):
    """
    Reads row of values for given satellite module name. Also return used range of simulation seconds.
    """
    with open(csv_path, "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        
        header = row_reader.__next__()
        second_range = None
        
        start_second = int(header[1])
        end_second = int(header[-1])
        second_range = list(range(start_second, end_second + 1))

        vals = None
        for row in row_reader:
            if row[0] == modname:
                vals = [ float(v) for v in row[1:] ]
                break
        
        if not vals:
            raise NameError(f"No values for satellite module {modname} could be found!")
        
        return vals, second_range