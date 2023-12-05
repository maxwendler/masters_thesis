import os
import json
import numpy as np
from scipy.interpolate import interp1d
from math import sqrt

def root_mean_square_error(list1, list2):
    if len(list1) != len(list2):
        raise AssertionError("Both input lists must have the same length!")
    
    square_error_sum = 0
    for i in range(len(list1)):
        square_error_sum += (list1[i] - list2[i]) * (list1[i] - list2[i])
    
    mean_square_error = square_error_sum / len(list1)
    return sqrt(mean_square_error) 

periods_dirs = [
    "/workspaces/ma-max-wendler/examples/space_veins/stats/comm_periods/eccentric/kepler",
    "/workspaces/ma-max-wendler/examples/space_veins/stats/comm_periods/eccentric/sgp4",
    "/workspaces/ma-max-wendler/examples/space_veins/stats/comm_periods/iridiumNEXT/kepler",
    "/workspaces/ma-max-wendler/examples/space_veins/stats/comm_periods/iridiumNEXT/kepler"
]

interpolation_schemes = [
    "linear",
    "zero",
    "slinear",
    "quadratic",
    "cubic"
]

angle_root_mean_square_errors = {}
distance_root_mean_square_errors = {}
delay_root_mean_square_errors = {}

for scheme in interpolation_schemes:
    angle_root_mean_square_errors[scheme] = []
    distance_root_mean_square_errors[scheme] = []
    delay_root_mean_square_errors[scheme] = []

for dir in periods_dirs:

    periods_paths = [dir + "/" + fname for fname in os.listdir(dir)]
    
    for json_path in periods_paths:
        
        with open(json_path, "r") as json_f:
            period_stats = json.load(json_f)
        
        # even duration => odd amount of values for angles, distances, delays
        # e.g. 2: 0, 1, 2
        odd_period_idxs = []
        for i in range(len(period_stats["durations"])):
            duration = period_stats["durations"][i]
            if duration % 2 == 0:
                odd_period_idxs.append(i)
        
        for period_idx in odd_period_idxs:
            odd_p_angles = period_stats["angles"][period_idx]
            odd_p_distances = period_stats["distances"][period_idx]
            odd_p_delays = period_stats["delays"][period_idx]

            # create test list to be interpolated where only every second value between start and end of list is used
            # for this, an odd number of entries is required (1st,3rd,5th,7th,9th,...)
            odd_p_angles_test = [odd_p_angles[0]]
            odd_p_distances_test = [odd_p_distances[0]]
            odd_p_delays_test = [odd_p_delays[0]]

            for i in range(2, len(odd_p_angles), 2):
                odd_p_angles_test.append(odd_p_angles[i])
                odd_p_distances_test.append(odd_p_distances[i])
                odd_p_delays_test.append(odd_p_delays[i])
            
            odd_p_test_xs = np.linspace(0, 1, len(odd_p_angles_test))
            odd_p_xs = np.linspace(0, 1, len(odd_p_angles))
            
            for scheme in interpolation_schemes:
                
                angle_interpolator = interp1d(odd_p_test_xs, odd_p_angles_test, kind=scheme)
                odd_p_angles_test_interp = list(angle_interpolator(odd_p_xs))
                angle_root_mean_square_errors[scheme].append( root_mean_square_error(odd_p_angles, odd_p_angles_test_interp) )                

                distance_interpolator = interp1d(odd_p_test_xs, odd_p_distances_test, kind=scheme)
                odd_p_distances_test_interp = list(distance_interpolator(odd_p_xs))
                distance_root_mean_square_errors[scheme].append( root_mean_square_error(odd_p_distances, odd_p_distances_test_interp) )
                
                delay_interpolator = interp1d(odd_p_test_xs, odd_p_delays_test, kind=scheme)
                odd_p_delays_test_interp = list(delay_interpolator(odd_p_xs))
                delay_root_mean_square_errors[scheme].append( root_mean_square_error(odd_p_delays, odd_p_delays_test_interp) )

avg_angle_root_mean_square_errors = {}
avg_distance_root_mean_square_errors = {}
avg_delay_root_mean_square_errors = {}

for scheme in interpolation_schemes:
    avg_angle_root_mean_square_errors[scheme] = sum(angle_root_mean_square_errors[scheme]) / len(angle_root_mean_square_errors[scheme])
    avg_distance_root_mean_square_errors[scheme] = sum(distance_root_mean_square_errors[scheme]) / len(distance_root_mean_square_errors[scheme])
    avg_delay_root_mean_square_errors[scheme] = sum(delay_root_mean_square_errors[scheme]) / len(delay_root_mean_square_errors[scheme])

output = {
    "angles": avg_angle_root_mean_square_errors,
    "distances": avg_distance_root_mean_square_errors,
    "delays": avg_delay_root_mean_square_errors
}

with open("./evaluate_interpolations_out.json", "w") as out_f:
    json.dump(output, out_f, indent=4)