import argparse
import os
from satname_to_modname import satname_to_modname
import re
import csv
from math import dist
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog="positional_differences.py", description="Outputs differences between coordinates of the specified trace files and result csvs.")

parser.add_argument("traces_or_csv_path", help="Path of directory traces of a constellation (should only contain traces of the constellation).")
parser.add_argument("csv_path", help="Path of directory with sgp4 result csvs of the constellation (can contain csvs of other constellations).")
parser.add_argument("constellation", help="Name of constellation to match file names.")
parser.add_argument("frame", help="Specifies coordinate reference frame. Requires one of: itrf, wgs84")
parser.add_argument("-d","--debug", action="store_true", help="If flag is set, result csvs of the form 'Debug-{constellation} will be matched.")
parser.add_argument("-c", "--coord_comp", action="store_true", help="If flag is set, distances in individual coordinate dimensions will be output, which is the only thing that currently can be calculated for wgs84 coordinates.")

args = parser.parse_args()

constellation_match_str = ""
if args.debug:
    constellation_match_str += "Debug-"
constellation_match_str += args.constellation
 
# if file at traces_or_csv_path is csv, parse csv
comparison_csv_coords = {}
is_csv2csv = False
if args.traces_or_csv_path.endswith(".csv"):
    is_csv2csv = True
    with open(args.traces_or_csv_path) as csv_f:
        first_row_reader = csv.DictReader(csv_f, delimiter="\t")
        first_row = first_row_reader.__next__()
        
        # in same order as in header
        coord_field_names = list(filter(lambda col_name: col_name.endswith("_vector"), first_row.keys()))
        # needs reordering for wgs84
        if args.frame == "wgs84":
            coord_field_names_sorted = []
            coord_field_names_sorted.append(filter(lambda col_name: "CoordLat" in col_name, coord_field_names).__next__())
            coord_field_names_sorted.append(filter(lambda col_name: "CoordLon" in col_name, coord_field_names).__next__())
            coord_field_names_sorted.append(filter(lambda col_name: "CoordAlt" in col_name, coord_field_names).__next__())
            coord_field_names = coord_field_names_sorted

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
                    comparison_csv_coords[current_mod] = current_mod_3d_coords

                # setup new current_mod with coords from current line
                current_mod = row["node"]
                current_mod_3d_coords = {}
                current_mod_3d_coords = [   (float(row[coord_field_names[0]]), 
                                            float(row[coord_field_names[1]]), 
                                            float(row[coord_field_names[2]]) ) ]
        
        # save results to dict after last row
        comparison_csv_coords[current_mod] = current_mod_3d_coords

# create leo-modname to satname mapping to find trace files
modname_to_satname_dict = {}

if not is_csv2csv:
    satnames = [traces_fname.removesuffix(".trace") for traces_fname in os.listdir(args.traces_or_csv_path)]
    for sname in satnames:
        modname_to_satname_dict[satname_to_modname(sname)] = sname

# find match for every module occuring in csv
modname_re = r"leo.*]"
distance_csv_lines = []

with open(args.csv_path, "r") as csv_f:
    first_row_reader = csv.DictReader(csv_f, delimiter="\t")
    first_row = first_row_reader.__next__()
    start_second = int(first_row["time"])
    
    # in same order as in header
    coord_field_names = list(filter(lambda col_name: col_name.endswith("_vector"), first_row.keys()))
    # needs reordering for wgs84
    if args.frame == "wgs84":
        coord_field_names_sorted = []
        coord_field_names_sorted.append(filter(lambda col_name: "CoordLat" in col_name, coord_field_names).__next__())
        coord_field_names_sorted.append(filter(lambda col_name: "CoordLon" in col_name, coord_field_names).__next__())
        coord_field_names_sorted.append(filter(lambda col_name: "CoordAlt" in col_name, coord_field_names).__next__())
        coord_field_names = coord_field_names_sorted

    csv_f.seek(0)

    reader = csv.DictReader(csv_f, delimiter="\t")
    current_mod = ""
    current_mod_3d_coords = []

    trace_file = None
    traces_path = None
    if not args.traces_or_csv_path.endswith(".csv"):
        traces_path = args.traces_or_csv_path if args.traces_or_csv_path.endswith("/") else args.traces_or_csv_path + "/"
    
    for row in reader:
        
        if row["node"] == current_mod:
            current_mod_3d_coords.append( (float(row[coord_field_names[0]]), 
                                           float(row[coord_field_names[1]]), 
                                           float(row[coord_field_names[2]]) ) )
        else:
            if current_mod != "":
                ### calc differences for old current_mod ###
                mod_leoname = re.search(modname_re, current_mod).group()
                
                if is_csv2csv:
                    
                    other_csv_current_mod_coords = comparison_csv_coords[current_mod]
                    if len(other_csv_current_mod_coords) != len(current_mod_3d_coords):
                        error_str = f"One CSV ({args.traces_or_csv_path}) has {len(other_csv_current_mod_coords)} per module, while the other one ({args.csv_path}) has {len(current_mod_3d_coords)}!"
                        raise AssertionError(error_str)
                    
                    distances = []
                    coord_comp_distances = {
                        coord_field_names[0]: [],
                        coord_field_names[1]: [],
                        coord_field_names[2]: []
                    }

                    for i in range(0, len(current_mod_3d_coords)):
                        
                        if args.frame == "itrf":
                            euklid_dist = dist(other_csv_current_mod_coords[i], current_mod_3d_coords[i])
                            distances.append(euklid_dist)
                        else:
                            distances.append(0)

                        if args.coord_comp:
                            for j in range(0, 3):
                                dimension_dist = abs(other_csv_current_mod_coords[i][j] - current_mod_3d_coords[i][j])
                                coord_comp_distances[coord_field_names[j]].append(dimension_dist)

                else:

                    # open (new) trace file
                    if trace_file:
                        if not trace_file.closed:
                            trace_file.close()
                    trace_path = traces_path + modname_to_satname_dict[mod_leoname] + ".trace"
                    trace_file = open(trace_path)
                    # read coordinates from trace (skipping to entry of second n at (n + 1)th line because of name in line one => idx n)
                    trace_coords = trace_file.readlines()[start_second:]
                    if len(trace_coords) != len(current_mod_3d_coords):
                        error_str = f"Trace file does not contain same number of values from start second {str(start_second)} at index {str(start_second)}: {len(trace_coords)} in trace, {len(current_mod_3d_coords)} in csv"
                        raise IndexError(error_str)

                    distances = []
                    coord_comp_distances = {
                        coord_field_names[0]: [],
                        coord_field_names[1]: [],
                        coord_field_names[2]: []
                    }

                    for i in range(0, len(trace_coords)):
                        trace_line_coords = list(map(lambda coord_comp: float(coord_comp.strip()), trace_coords[i].split(",")))
                        
                        if args.frame == "itrf":
                            euklid_dist = dist(trace_line_coords, current_mod_3d_coords[i])
                            distances.append(euklid_dist)
                        else:
                            distances.append(0)
                        
                        if args.coord_comp:
                            for j in range(0, len(trace_line_coords)):
                                dimension_dist = abs(trace_line_coords[j] - current_mod_3d_coords[i][j])
                                coord_comp_distances[coord_field_names[j]].append(dimension_dist)

                if len(distance_csv_lines) == 0:
                    csv_header = "sat_name"
                    for i in range(start_second, start_second + len(distances)):
                        csv_header += "," + str(i)
                    distance_csv_lines.append(csv_header)

                mod_distances_str = mod_leoname
                for d in distances:
                   mod_distances_str += "," + str(d) 
                distance_csv_lines.append(mod_distances_str)

                if args.coord_comp:
                    for coord_dim in coord_field_names:
                        coord_dim_distances_str = mod_leoname + "_" + coord_dim
                        for d in coord_comp_distances[coord_dim]:
                            coord_dim_distances_str += "," + str(d)
                        distance_csv_lines.append(coord_dim_distances_str)

            # setup new current_mod wiht coords from current line
            current_mod = row["node"]
            current_mod_3d_coords = [   (float(row[coord_field_names[0]]), 
                                        float(row[coord_field_names[1]]), 
                                        float(row[coord_field_names[2]]) ) ]

#with open("/workspaces/ma-max-wendler/scripts/plots/test_output/" + args.constellation + "_" + args.frame + "_distances_keplersgp4.csv", "w") as new_csv_f:
#    new_csv_f.write("\n".join(distance_csv_lines))

print("\n".join(distance_csv_lines))