import argparse
import os
from satname_to_modname import satname_to_modname
import re
import csv
from math import dist
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog="positional_differences.py", description="Outputs differences between coordinates of the specified trace files and result csvs.")

parser.add_argument("traces_path", help="Path of directory traces of a constellation (should only contain traces of the constellation).")
parser.add_argument("csv_path", help="Path of directory with sgp4 result csvs of the constellation (can contain csvs of other constellations).")
parser.add_argument("constellation", help="Name of constellation to match file names.")
parser.add_argument("-d","--debug", action="store_true", help="If flag is set, result csvs of the form 'Debug-{constellation} will be matched.")
parser.add_argument("-f","--frame", help="Specifies coordinate reference frame. Requires one of: itrf, wgs84")
parser.add_argument("-c", "--coord_comp", action="store_true", help="If flag is set, distances in individual component dimensions will be output.")

args = parser.parse_args()

constellation_match_str = ""
if args.debug:
    constellation_match_str += "Debug-"
constellation_match_str += args.constellation

"""
result_csv_names = []
for csv_name in os.listdir(args.csvs_path):
    if args.frame in csv_name and constellation_match_str in csv_name:
        print(args.frame)
        print(constellation_match_str)
        result_csv_names.append(csv_name)

if len(result_csv_names) != 1:
    error_str = f"Expected one result files for 3d coordinates, but found {len(result_csv_names)}! \n {str(result_csv_names)}"
    print(len(result_csv_names))
    raise AssertionError(error_str)


if args.frame == "wgs84":
    for coord in ["CoordAlt","CoordLat", "CoordLon"]:
        found_coord = False
        for csv_name in result_csv_names:
            if coord in csv_name:
                found_coord = True
                break
        if not found_coord:
            raise AssertionError(f"No result csv for wgs84 {coord} found!")
elif args.frame == "itrf":
    coords = ["CoordX","CoordY", "CoordZ"]
    for coord in coords:
        found_coord = False
        for csv_name in result_csv_names:
            if coord in csv_name:
                found_coord = True
                break
        if not found_coord:
            raise AssertionError(f"No result csv for itrs {coord} found!")
else:
    raise ValueError(f"This script does not support {args.frame} coordinate frame, only wgs84 and itrf!")
"""

 
# create leo-modname to satname mapping
satnames = [traces_fname.removesuffix(".trace") for traces_fname in os.listdir(args.traces_path)]
modname_to_satname_dict = {}
for sname in satnames:
    modname_to_satname_dict[satname_to_modname(sname)] = sname

# find match for every module occuring in csv
# test_path = args.csv_path
modname_re = r"leo.*]"

with open(args.csv_path, "r") as csv_f:
    print(csv_f)
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
    traces_path = args.traces_path if args.traces_path.endswith("/") else args.traces_path + "/"
    distance_csv_lines = []
    for row in reader:
        
        if row["node"] == current_mod:
            current_mod_3d_coords.append( (float(row[coord_field_names[0]]), 
                                           float(row[coord_field_names[1]]), 
                                           float(row[coord_field_names[2]]) ) )
            # print(row)
            # print("current num of csv coords:", len(current_mod_3d_coords))
        else:
            if current_mod != "":
                ### calc differences for old current_mod ###
                mod_leoname = re.search(modname_re, current_mod).group()
                # open (new) trace file
                if trace_file:
                    if not trace_file.closed:
                        trace_file.close()
                trace_path = traces_path + modname_to_satname_dict[mod_leoname] + ".trace"
                trace_file = open(trace_path)
                # read coordinates from trace (skipping to entry of second n at (n + 1)th line because of name in line one => idx n)
                trace_coords = trace_file.readlines()[start_second:]
                if len(trace_coords) != len(current_mod_3d_coords):
                    print("Trace path:", trace_path)
                    print("current num of csv coords:", len(current_mod_3d_coords))
                    error_str = f"Trace file does not contain same number of values from start second {str(start_second)} at index {str(start_second)}: {len(trace_coords)} in trace, {len(current_mod_3d_coords)} in csv"
                    raise IndexError(error_str)

                distances = []
                coord_comp_distances = {
                    coord_field_names[0]: [],
                    coord_field_names[1]: [],
                    coord_field_names[2]: []
                }

                print("***")
                print(current_mod)
                print(len(trace_coords))
                for i in range(0, len(trace_coords)):
                    print("trace_coords:",trace_coords[i])
                    trace_line_coords = list(map(lambda coord_comp: float(coord_comp.strip()), trace_coords[i].split(",")))
                    euklid_dist = dist(trace_line_coords, current_mod_3d_coords[i])
                    distances.append(euklid_dist)
                    
                    for j in range(0, len(trace_line_coords)):
                        dimension_dist = abs(trace_line_coords[j] - current_mod_3d_coords[i][j])
                        coord_comp_distances[coord_field_names[j]].append(dimension_dist)

                    if i == 0:
                        print("---")
                        print(trace_line_coords)
                        print(current_mod_3d_coords[i])
                        print(coord_comp_distances[coord_field_names[0]][i], coord_comp_distances[coord_field_names[1]][i], coord_comp_distances[coord_field_names[2]][i])
                    
                    if args.frame == "itrf":
                        print(euklid_dist)

                plt.plot(range(start_second, start_second + len(trace_coords)), distances)
                plt.ylabel("difference")
                plt.xlabel("simulation second")
                
                # plt.savefig(f'/workspaces/ma-max-wendler/scripts/plots/test_output/{mod_leoname}_{args.frame}_distances.png', transparent=False, dpi=80, bbox_inches='tight')
                # plt.show()
                plt.clf()

                if len(distance_csv_lines) == 0:
                    csv_header = "sat_name"
                    for i in range(start_second, start_second + len(distances)):
                        #csv_header += "," + "sim. s " + str(i)
                        csv_header += "," + str(i)
                    distance_csv_lines.append(csv_header)

                mod_distances_str = mod_leoname
                for d in distances:
                   mod_distances_str += "," + str(d) 
                distance_csv_lines.append(mod_distances_str)

                if args.coord_comp:
                    for coord_dim in coord_field_names:
                        coord_dim_distances_str = coord_dim
                        for d in coord_comp_distances[coord_dim]:
                            coord_dim_distances_str += "," + str(d)
                        distance_csv_lines.append(coord_dim_distances_str)

            # setup new current_mod wiht coords from current line
            current_mod = row["node"]
            current_mod_3d_coords = [   (float(row[coord_field_names[0]]), 
                                        float(row[coord_field_names[1]]), 
                                        float(row[coord_field_names[2]]) ) ]

    with open("/workspaces/ma-max-wendler/scripts/plots/test_output/" + args.constellation + "_" + args.frame + "_distances_keplersgp4.csv", "w") as new_csv_f:
        new_csv_f.write("\n".join(distance_csv_lines))

    """
    current_mod = ""
    remaining_mod_entries = 0
    for line in csv_f.readlines():
        if remaining_mod_entries = 0:
        line_modname = re.search(modname_re, line)
        if line_modname != None:
            line_modname = line_modname.group()
            print(line)
            print(line_modname)
            print(modname_to_satname_dict[line_modname])
    """