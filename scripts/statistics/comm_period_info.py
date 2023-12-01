import argparse
import csv
import json
import os

def get_communication_periods(angles: list[float], min_angle: float, start_sec: float, step: float) -> list[tuple[float, float]]:
    
    comm_periods = []
    per_start_sec = None
    per_end_sec = None
    comm_possible = False
    
    for i in range(0, len(angles)):
        current_sec = start_sec + i * step
        angle = angles[i]

        # communication becomes or remains possible
        if angle >= min_angle:
            
            # comm. becomes possible
            if not comm_possible:
                per_start_sec = current_sec
                comm_possible = True
            # else: comm. remains possible
        
        # communication becomes or remains impossible
        else:

            # communication becomes impossible
            if comm_possible:
                per_end_sec = current_sec - 1
                comm_periods.append( (per_start_sec, per_end_sec) )
                comm_possible = False
            
            # else: communication remains impossible
    
    return comm_periods

def get_mod_csv_row_vals(csv_path: str, modname: str) -> tuple[list[float], list[int]]:
    with open(csv_path, "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        
        header = row_reader.__next__()
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="comm_period_info", description="Isolates the elevation angle, distance and delay w.r.t. SOP from the given csvs and writes them to a JSON.")
    parser.add_argument("angles_csv_path")
    parser.add_argument("distances_csv_path")
    parser.add_argument("delays_csv_path")
    parser.add_argument("tle_times_path")
    parser.add_argument("modname")
    parser.add_argument("min_angle", type=float)
    parser.add_argument("output_path")
    args = parser.parse_args()

    tle_times = None
    with open(args.tle_times_path, "r") as times_f:
        tle_times = json.load(times_f) 
    mod_epoch_to_start_offset_days = float(tle_times["sat_times"][args.modname]["offset_to_start"])
    mod_epoch_to_start_offset_secs = mod_epoch_to_start_offset_days * 86400

    angles, second_range = get_mod_csv_row_vals(args.angles_csv_path, args.modname)
    periods = get_communication_periods(angles, args.min_angle, second_range[0], 1)
    distances, second_range = get_mod_csv_row_vals(args.distances_csv_path, args.modname)
    delays, second_range = get_mod_csv_row_vals(args.delays_csv_path, args.modname)

    periods_angles = []
    periods_delays = []
    periods_distances = []
    period_start_offsets = []

    for p in periods:
        
        start_sec = p[0]
        end_sec = p[1]
        period_start_to_epoch_offset = start_sec - mod_epoch_to_start_offset_secs

        periods_angles.append(angles[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])])
        periods_distances.append(distances[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])])
        periods_delays.append(delays[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])])
        period_start_offsets.append(period_start_to_epoch_offset)

    mobility = args.output_path.split("/")[-2]
    communication_period_dict = {"modname": args.modname, 
                                "mobility": mobility, 
                                "periods": periods, 
                                "period_start_to_epoch_offsets": period_start_offsets, 
                                "angles": periods_angles,
                                "distances": periods_distances, 
                                "delays": periods_delays }

    output_dir = "/".join(args.output_path.split("/")[:-1])
    os.makedirs(output_dir, exist_ok=True)
    with open(args.output_path, "w") as output_f:
        json.dump(communication_period_dict, output_f, indent=4)