import argparse
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_dict
from math import dist

parser = argparse.ArgumentParser()
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