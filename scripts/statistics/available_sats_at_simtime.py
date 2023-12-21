import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("comm_period_jsons_dir")
parser.add_argument("measurement_start_time", type=int)
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("ouput_path")
args = parser.parse_args()

comm_periods_jsons_dir = args.comm_period_jsons_dir if args.comm_period_jsons_dir.endswith("/") else args.comm_period_jsons_dir + "/"

comm_period_dicts = []
for comm_period_json_fname in os.listdir(comm_periods_jsons_dir):
    
    comm_periods_path = comm_periods_jsons_dir + comm_period_json_fname
    with open(comm_periods_path, "r") as json_f:
        sat_comm_periods = json.load(json_f)
    
    modname = sat_comm_periods["modname"]
    for period in sat_comm_periods["periods"]:
        comm_period_dicts.append({"modname": modname, "period": period})

available_sats = []
for sim_time in range(args.measurement_start_time, args.sim_time_limit + 1):
    
    current_available_sats = []
    for comm_period_dict in comm_period_dicts:
        period = comm_period_dict["period"]
        if period[0] <= sim_time and sim_time <= period[1]:
            current_available_sats.append(comm_period_dict["modname"])
    
    available_sats.append({
        "sim_time": sim_time,
        "sat_num": len(current_available_sats),
        "sats": current_available_sats
    })

with open(args.ouput_path, "w") as out_json:
    json.dump(available_sats, out_json, indent=4)