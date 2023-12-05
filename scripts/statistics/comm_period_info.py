import argparse
import json
import sys, os
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import get_mod_row 

def get_communication_periods(angles: list[float], min_angle: float, start_sec: float, step: float) -> list[tuple[float, float]]:
    """
    Calculates list of periods of simulation seconds when communication is possible because the elevation angle exceeds the minimum elevation angle.
    """

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

def get_local_max_idx(angles, start_sec, zenith_time):
    zenith_idx = zenith_time - start_sec
    
    if zenith_idx == 0:
        return 0 
        
    local_max_idx = -1
    for i in range(zenith_idx):
        
        if i == 0:
            if angles[i] > angles[i + 1]:
                local_max_idx += 1
        elif i == zenith_idx - 1:
            pass            
        else:
            if angles[i - 1] < angles[i] and angles[i + 1] < angles[i]:
                local_max_idx += 1
    
    # +1 as iteration ends before zenith idx
    return local_max_idx + 1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="comm_period_info", 
                                     description="""Creates JSON of periods where communication is possible for the specified constellation, mobility and satellite module name,
                                    using minimum elevation angle 25 °.
                                    Each JSON contains the minimum elevation angles, distances and delays relative to the SOP for each communication period,
                                    as well as the offset to the used TLE's epoch.""")
    parser.add_argument("angles_csv_path", help="Path of CSV with elevation angles to SOP of the satellite module.")
    parser.add_argument("distances_csv_path", help="Path of CSV with distances to SOP of the satellite module.")
    parser.add_argument("delays_csv_path", help="Path of CSV with delays to SOP of the satellite module.")
    parser.add_argument("tle_times_path", help="Path of JSON with simulation start time and epoch times of TLEs in numpy's datetime64 format.")
    parser.add_argument("modname", help="Name of a satellite module.")
    parser.add_argument("min_angle", type=float, help="Minimum elevation angle determining if communication is possible.")
    parser.add_argument("output_path")
    args = parser.parse_args()

    # calculate offset of used TLE's epoch to simulation start time in seconds
    tle_times = None
    with open(args.tle_times_path, "r") as times_f:
        tle_times = json.load(times_f) 
    mod_epoch_to_start_offset_days = float(tle_times["sat_times"][args.modname]["offset_to_start"])
    mod_epoch_to_start_offset_secs = mod_epoch_to_start_offset_days * 86400

    angles, second_range = get_mod_row(args.angles_csv_path, args.modname)
    periods = get_communication_periods(angles, args.min_angle, second_range[0], 1)
    distances, second_range = get_mod_row(args.distances_csv_path, args.modname)
    delays, second_range = get_mod_row(args.delays_csv_path, args.modname)

    # create lists of lists with values for each communication period
    durations = []
    periods_angles = []
    periods_delays = []
    periods_distances = []
    period_start_offsets = []
    zenith_times = []
    local_max_idxs = []
    for p in periods:
        
        start_sec = p[0]
        end_sec = p[1]
        durations.append(end_sec - start_sec)
        period_start_to_epoch_offset = start_sec - mod_epoch_to_start_offset_secs

        period_angles = angles[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])]
        periods_angles.append(period_angles)

        # find zenith and index
        max_angle = 0
        zenith_idx = -1
        for angle_idx in range(len(period_angles)):
            angle = period_angles[angle_idx]
            if angle > max_angle:
                max_angle = angle
                zenith_idx = angle_idx
        
        # calc zenith time
        zenith_time = start_sec + zenith_idx
        zenith_times.append(zenith_time)

        # calculate n for: zenith is n-th local maximum of angles
        local_max_idxs.append(get_local_max_idx(angles, second_range[0], zenith_time))

        periods_distances.append(distances[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])])
        periods_delays.append(delays[(start_sec - second_range[0]):(end_sec + 1 - second_range[0])])
        period_start_offsets.append(period_start_to_epoch_offset)

    mobility = args.output_path.split("/")[-2]
    communication_period_dict = {"modname": args.modname, 
                                "mobility": mobility, 
                                "periods": periods,
                                "durations": durations,
                                "period_start_to_epoch_offsets": period_start_offsets,
                                "zenith_times": zenith_times,
                                "local_max_idxs": local_max_idxs, 
                                "angles": periods_angles,
                                "distances": periods_distances, 
                                "delays": periods_delays}

    output_dir = "/".join(args.output_path.split("/")[:-1])
    os.makedirs(output_dir, exist_ok=True)
    with open(args.output_path, "w") as output_f:
        json.dump(communication_period_dict, output_f, indent=4)