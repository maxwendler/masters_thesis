import argparse
import os
from satname_to_modname import satname_to_modname
import csv
from math import dist
import re

modname_re = r"leo.*]"

def sort_wgs84_coord_fieldnames(fieldnames: list[str]) -> list[str]:
    coord_field_names_sorted = []
    coord_field_names_sorted.append(filter(lambda col_name: "CoordLat" in col_name, fieldnames).__next__())
    coord_field_names_sorted.append(filter(lambda col_name: "CoordLon" in col_name, fieldnames).__next__())
    coord_field_names_sorted.append(filter(lambda col_name: "CoordAlt" in col_name, fieldnames).__next__())
    return coord_field_names_sorted

def parse_csv_coords(csv_path: str, frame: str) -> tuple[dict[str, list[tuple[float, float, float]]], int, list[str]]:
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

def parse_trace_coords(trace_path: str, start_second: int) -> list[tuple[float, float, float]]:
    coords_3d = []
    with open(trace_path, "r") as trace_f:
        # skip line with satellite name, hence not idx start_second - 1
        for coord in trace_f.readlines()[start_second:]:
            dimension_coords = [ float(c.strip()) for c in coord.split(",") ]
            coords_3d.append( tuple(dimension_coords) )
    return coords_3d

def parse_constellation_traces(traces_dir: str, start_second: int) -> dict[str, list[tuple[float, float, float]]]:
    if not traces_dir.endswith("/"):
        traces_dir += "/"
    coord_dict = {}
    for trace_fname in filter( lambda fname: fname.endswith(".trace"), os.listdir(traces_dir)):
        satname = trace_fname.removesuffix(".trace")
        leo_modname = satname_to_modname(satname)
        coord_dict[leo_modname] = parse_trace_coords(traces_dir + trace_fname, start_second)
    return coord_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="positional_differences.py", description="Outputs differences between coordinates of the specified trace files and result csvs.")

    parser.add_argument("traces_or_csv_path", help="Path of directory traces of a constellation (should only contain traces of the constellation).")
    parser.add_argument("csv_path", help="Path of directory with sgp4 result csvs of the constellation (can contain csvs of other constellations).")
    parser.add_argument("frame", choices=["itrf", "wgs84", "omnet"], help="Specifies coordinate reference frame. Requires one of.")
    parser.add_argument("-c", "--coord_dims", action="store_true", help="If flag is set, distances in individual coordinate dimensions will be output, which is the only thing that currently can be calculated for wgs84 coordinates.")

    args = parser.parse_args()

    traces_or_csv_path = args.traces_or_csv_path
    csv_path = args.csv_path
    frame = args.frame

    coord_dict_2, start_second, coord_field_names = parse_csv_coords(csv_path, frame)
    coord_dict_1 = None
    if "traces" in traces_or_csv_path:
        coord_dict_1 = parse_constellation_traces(traces_or_csv_path, start_second)
    else:
        coord_dict_1, _start_second, _coord_field_names = parse_csv_coords(traces_or_csv_path, frame)

    distance_csv_lines = []
    csv_header = "sat_name"
    coord_num = len(list(coord_dict_2.values())[0])
    for i in range(start_second, start_second + coord_num):
        csv_header += "," + str(i)
    distance_csv_lines.append(csv_header)

    for leo_modname in coord_dict_2.keys():
        
        mod_coords_1 = coord_dict_1[leo_modname]
        mod_coords_2 = coord_dict_2[leo_modname]
        if len(mod_coords_1) != len(mod_coords_2):
            error_str = f"First input file at {traces_or_csv_path} has {len(mod_coords_1)} coordinates from start second {start_second}, while second file at {csv_path} has {len(mod_coords_2)}!"
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
        
        mod_distances_str = leo_modname
        for d in dists:
            mod_distances_str += "," + str(d) 
        distance_csv_lines.append(mod_distances_str)

        if args.coord_dims:
            for coord_dim in coord_field_names:
                coord_dim_distances_str = leo_modname + "_" + coord_dim
                for d in dimension_dists[coord_dim]:
                    coord_dim_distances_str += "," + str(d)
                distance_csv_lines.append(coord_dim_distances_str)
        
    print("\n".join(distance_csv_lines))
    # output file for testing purposes
    #with open("/workspaces/ma-max-wendler/scripts/plots/test_output/debug_test.csv", "w") as new_csv_f:
    #    new_csv_f.write("\n".join(distance_csv_lines))