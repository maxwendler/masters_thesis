from tletools import TLE
import argparse
from datetime import datetime
from numpy import datetime64
from astropy.time import Time
import json
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.satname_to_modname import satname_to_modname

parser = argparse.ArgumentParser(prog="tletimes.py", description="Parses sim start time and TLE times of given TLE list into dict written to .json *_times.json at same location.")
parser.add_argument("tles_path")
args = parser.parse_args()
tles_path = args.tles_path

tles_fname = tles_path.split("/")[-1]
start_time_str = tles_fname.removesuffix(".txt").split("_")[-1]
start_time_dt = datetime.strptime(start_time_str, "%Y-%m-%d-%H-%M-%S")
start_time = Time(datetime64(start_time_dt), format="datetime64", scale="utc")

times_dict = {}
times_dict["start_time"] = str(start_time)

with open(tles_path, "r") as tles_f:
    lines = tles_f.readlines()   
    
    sat_times_dict = {}
    for i in range(0, len(lines), 3):
        
        tle = TLE.from_lines(lines[i], lines[i+1], lines[i+2])
        satname = tle.name
        modname = satname_to_modname(satname)
        tle.epoch.format = "datetime64"
        offset_to_start = tle.epoch - start_time
        offset_to_start.format = "sec"
        # offset_to_start.format = "datetime"
        sat_times_dict[modname] = {"epoch": str(tle.epoch), "offset_to_start": str(offset_to_start)}

    times_dict["sat_times"] = sat_times_dict

constellation = tles_fname.split("_")[0]
output_path = tles_path.removesuffix(tles_fname) + constellation + "_times.json"
with open(output_path, "w") as dict_f:
    json.dump(times_dict, dict_f, indent=4)    