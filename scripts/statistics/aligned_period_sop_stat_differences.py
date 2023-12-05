import argparse
import json
import numpy as np
from scipy.interpolate import interp1d, CubicSpline

parser = argparse.ArgumentParser(prog="aligned_period_sop_stat_differences", description="???")
parser.add_argument("comm_period_groups_path", help="Path of JSON that matches communication periods between reference mobility and alternative (new) mobility.")
parser.add_argument("ref_mobility", help="Name of reference mobility.")
parser.add_argument("ref_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("new_mobility", help="Name of the alternative (new) mobility.")
parser.add_argument("new_mobility_periods_path", help="Path of the JSON with communication periods of the reference mobility and their elevations angles, distances and delays relative to the SOP.")
parser.add_argument("output_path", help="Path where result JSON will be written to.")
parser.add_argument("--changes", help="If flag is set, calculates changes from reference mobility to alternative (new) mobility instead of differences.")
args = parser.parse_args()

### load communication period statistics ###
ref_mobility = args.ref_mobility
ref_mobility_stats = None
with open(args.ref_mobility_periods_path, "r") as in_json:
    ref_mobility_stats = json.load(in_json)
new_mobility = args.new_mobility
new_mobility_stats = None
with open(args.new_mobility_periods_path, "r") as in_json:
    new_mobility_stats = json.load(in_json)

# load communication period comparison
comm_periods = {}
with open(args.comm_period_groups_path, "r") as in_json:
    comm_periods = json.load(in_json)

period_groups = comm_periods["period_groups"]

output = {"modname": comm_periods["modname"],
          "period_groups": []}
for p_group in period_groups:
    # copy period start and end and mobility period idx
    new_p_group_dict = {ref_mobility: p_group[ref_mobility],
                        new_mobility: p_group[new_mobility]}

    # aligned difference / change calculation for range of shorter period
    ref_angles = ref_mobility_stats["angles"][ p_group[ref_mobility]["period_idx"] ]
    ref_idxs = np.linspace(0, 1, len(ref_angles))
    new_angles = new_mobility_stats["angles"][ p_group[new_mobility]["period_idx"] ]
    new_idxs = np.linspace(0, 1, len(new_angles))

    # interpolate to length of shorter list => do not extrapolate
    if len(ref_angles) < len(new_angles):
        print("interpolating new angles")
        f_cubic = CubicSpline(new_idxs, new_angles)
        f_lin = interp1d(new_idxs, new_angles)
        ref_angles_interp = list(f_lin(ref_idxs))
        print("done")

    else:
        print("interpolating ref angles")
        f_cubic = CubicSpline(new_idxs, new_angles)
        interpolated_ref_angles = f_cubic(ref_angles)
        print(ref_angles)
        print(interpolated_ref_angles)
        print(len(interpolated_ref_angles), len(new_angles))

    output["period_groups"].append(new_p_group_dict)
    break