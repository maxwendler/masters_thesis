import argparse
import sys, os
from math import dist
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_dict

parser = argparse.ArgumentParser()
parser.add_argument("sgp4_pos_csv")
parser.add_argument("output_path")
args = parser.parse_args()

pos_dict, start_second, coord_field_names = parse_coords_csv_to_dict(args.sgp4_pos_csv, "teme")

avgalt_csv_lines = []
avgalt_csv_lines.append("modname,avg_altitude")
for modname in pos_dict.keys():
    
    alt_sum = 0
    positions = pos_dict[modname]
    for pos in positions:
        alt_sum += dist((0, 0, 0), pos)
    avg_alt = alt_sum / len(positions)

    avgalt_csv_lines.append( modname + "," + str(avg_alt))

with open(args.output_path, "w") as out_csv:
    out_csv.write("\n".join(avgalt_csv_lines))
