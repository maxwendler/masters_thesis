import argparse
from positional_differences import parse_csv_coords
from math import dist, acos
import astropy.units as u
from astropy.coordinates import Angle

parser = argparse.ArgumentParser(prog="sop_stats.py",description="Calulcates satellite elevation angle, satelitte distance to SOP, and propagation delay from given omnetCoord csv.")
parser.add_argument("csv_path")
parser.add_argument("sop_coord", nargs=3, type=float)
parser.add_argument("output_dir")
parser.add_argument("-e", "--eval_angle", type=float, help="Only calculate propgation delay when communication is possible with given minimum elevation angle (float). Entry is 0 otherwise.")
args = parser.parse_args()
output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"
output_base_fname = args.csv_path.split("/")[-1].removesuffix("_omnet_sorted.csv")

sat_coord_dict, start_second, _coord_field_names = parse_csv_coords(args.csv_path, frame="omnet")
min_eval_angle = args.eval_angle
sop_coord = args.sop_coord

header = "modname"
for i in range(start_second, start_second + len(list(sat_coord_dict.values())[0])):
    header += "," + str(i)

distance_csv_lines = [header]
elev_angles_csv_lines = [header]
propagation_delay_csv_lines = [header]

for satname in sat_coord_dict.keys():
    
    sop_sat_distances = [] 
    sop_sat_elev_angles = []
    sat_propagation_delays = []
    for i in range(0, len(sat_coord_dict[satname]) ):
        
        sat_coord = sat_coord_dict[satname][i]

        # calc distance
        distance = dist(sop_coord, sat_coord)
        sop_sat_distances.append( distance )

        # calc angle to omnet x(east)y(north) plane
        # up coord is 0
        vec_in_plane = ( sat_coord[0] - sop_coord[0], sat_coord[1] - sop_coord[1], 0 )
        dot_product = sat_coord[0] * vec_in_plane[0] + sat_coord[1] * vec_in_plane[1] + sat_coord[2] * vec_in_plane[2]
        angle_to_plane_rad = Angle(acos( (dot_product) / (dist(vec_in_plane, sop_coord) * dist(sat_coord, sop_coord)) ), u.rad)
        angle_to_plane_deg = angle_to_plane_rad.degree

        # if 'up' coordinate is negative, angle will be negative
        elev_angle = angle_to_plane_deg
        if sat_coord[2] < 0:
            elev_angle *= -1
        sop_sat_elev_angles.append( elev_angle )

        delay = 0
        if elev_angle > min_eval_angle or not args.eval_angle:
            # *.radioMedium.propagation.propagationSpeed = 299792458 mps # speed of light
            delay = distance / 299792.458
        sat_propagation_delays.append(delay)

    new_line = satname
    for d in sop_sat_distances:
        new_line += "," + str(d)
    distance_csv_lines.append(new_line)

    new_line = satname
    for a in sop_sat_elev_angles:
        new_line += "," + str(a)
    elev_angles_csv_lines.append(new_line)

    new_line = satname
    for d in sat_propagation_delays:
        new_line += "," + str(d)
    propagation_delay_csv_lines.append(new_line)


distances_path = output_dir + output_base_fname + "_distances.csv"
with open(distances_path, "w") as csv_f:
    csv_f.write( "\n".join(distance_csv_lines) )

angles_path = output_dir + output_base_fname + "_angles.csv"
with open(angles_path, "w") as csv_f:
    csv_f.write( "\n".join(elev_angles_csv_lines) )

propagation_delay_path = output_dir + output_base_fname + "_delays.csv"
with open(propagation_delay_path, "w") as csv_f:
    csv_f.write( "\n".join(propagation_delay_csv_lines) )