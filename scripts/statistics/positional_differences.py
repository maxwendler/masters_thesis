import argparse
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_dict
from math import dist
import csv
import re

modname_re = r"leo.*]"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="positional_differences.py", description="Outputs differences between coordinates of the specified trace files and result csvs.")

    parser.add_argument("csv_path1", help="Path of directory with kepler result csvs of the constellation (can contain csvs of other constellations).")
    parser.add_argument("csv_path2", help="Path of directory with sgp4 result csvs of the constellation (can contain csvs of other constellations).")
    parser.add_argument("frame", choices=["itrf", "wgs84", "omnet", "teme"], help="Specifies coordinate reference frame. Requires one of.")
    parser.add_argument("-c", "--coord_dims", action="store_true", help="If flag is set, distances in individual coordinate dimensions will be output, which is the only thing that currently can be calculated for wgs84 coordinates.")

    args = parser.parse_args()

    csv_path1 = args.csv_path1
    csv_path2 = args.csv_path2
    frame = args.frame

    # coord_dict_2, start_second, coord_field_names = parse_coords_csv_to_dict(csv_path2, frame)
    coord_dict_1, start_second, coord_field_names = parse_coords_csv_to_dict(csv_path1, frame)

    # create header for all coords in a row of satellite module name
    distance_csv_lines = []
    csv_header = "sat_name"
    coord_num = len(list(coord_dict_1.values())[0])
    for i in range(start_second, start_second + coord_num):
        csv_header += "," + str(i)
    distance_csv_lines.append(csv_header)

    with open(csv_path2, "r") as csv2_f:
        dict_reader = csv.DictReader(csv2_f, delimiter="\t")
        # skip header
        # dict_reader.__next__()

        current_mod = ""
        current_leo_modname = ""
        mod_coords_2 = []

        for row in dict_reader:
            if row["node"] == current_mod:
                mod_coords_2.append( (float(row[coord_field_names[0]]), 
                                                float(row[coord_field_names[1]]), 
                                                float(row[coord_field_names[2]]) ) )
            
            else:
                if current_mod != "":
                    # calculate differences
                    mod_coords_1 = coord_dict_1[current_leo_modname]

                    if len(mod_coords_1) != len(mod_coords_2):
                        error_str = f"First input file at {csv_path1} has {len(mod_coords_1)} coordinates from start second {start_second}, while second file at {csv_path2} has {len(mod_coords_2)}!"
                        raise AssertionError(error_str)

                    dists = []
                    dimension_dists = {coord_field_names[0]: [],
                                    coord_field_names[1]: [],
                                    coord_field_names[2]: []}
                    
                    for i in range(0, len(mod_coords_1)):
                        
                        dists.append(dist(mod_coords_1[i], mod_coords_2[i]))
                        
                        if args.coord_dims:
                            for j in range(0, 3):
                                dimension_dists[coord_field_names[j]].append( abs(mod_coords_1[i][j] - mod_coords_2[i][j]) )
                    
                    mod_distances_str = current_leo_modname
                    for d in dists:
                        mod_distances_str += "," + str(d) 
                    distance_csv_lines.append(mod_distances_str)

                    # optionally create rows for individual dimensions of 3d coordinates
                    if args.coord_dims:
                        for coord_dim in coord_field_names:
                            coord_dim_distances_str = current_leo_modname + "_" + coord_dim
                            for d in dimension_dists[coord_dim]:
                                coord_dim_distances_str += "," + str(d)
                            distance_csv_lines.append(coord_dim_distances_str)

                # setup new current_mod with coords from current line
                current_mod = row["node"]
                current_leo_modname = re.search(modname_re, row["node"]).group()
                mod_coords_2 = {}
                mod_coords_2 = [   (float(row[coord_field_names[0]]), 
                                            float(row[coord_field_names[1]]), 
                                            float(row[coord_field_names[2]]) ) ]        
    
    # calculate differences after last row 
    # calculate differences
    mod_coords_1 = coord_dict_1[current_leo_modname]

    if len(mod_coords_1) != len(mod_coords_2):
        error_str = f"First input file at {csv_path1} has {len(mod_coords_1)} coordinates from start second {start_second}, while second file at {csv_path2} has {len(mod_coords_2)}!"
        raise AssertionError(error_str)

    dists = []
    dimension_dists = {coord_field_names[0]: [],
                    coord_field_names[1]: [],
                    coord_field_names[2]: []}
    
    for i in range(0, len(mod_coords_1)):
        
        dists.append(dist(mod_coords_1[i], mod_coords_2[i]))
        
        if args.coord_dims:
            for j in range(0, 3):
                dimension_dists[coord_field_names[j]].append( abs(mod_coords_1[i][j] - mod_coords_2[i][j]) )
    
    mod_distances_str = current_leo_modname
    for d in dists:
        mod_distances_str += "," + str(d) 
    distance_csv_lines.append(mod_distances_str)

    # optionally create rows for individual dimensions of 3d coordinates
    if args.coord_dims:
        for coord_dim in coord_field_names:
            coord_dim_distances_str = current_leo_modname + "_" + coord_dim
            for d in dimension_dists[coord_dim]:
                coord_dim_distances_str += "," + str(d)
            distance_csv_lines.append(coord_dim_distances_str)

    print("\n".join(distance_csv_lines))