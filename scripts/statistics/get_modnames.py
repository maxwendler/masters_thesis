import os
import sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.satname_to_modname import satname_to_modname
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tles_path")
parser.add_argument("output_path")
args = parser.parse_args()

modnames = []
with open(args.tles_path, "r") as tles_f:
    lines = tles_f.readlines()
    for i in range(0, len(lines), 3):
        satname = lines[i].removesuffix("\n")
        modnames.append(satname_to_modname(satname))

with open(args.output_path, "w") as out_f:
    out_f.write("\n".join(modnames))