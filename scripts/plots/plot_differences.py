import argparse
import csv
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog="plot_differences.py", description="Plots the differences of specified satellite modules from specified CSV.")

parser.add_argument("csv_path", help="Path of csv file with (distance SGP4/Kepler at sim. second) vectors per satellite module.")
parser.add_argument('sat_mods', metavar='leo_modname', type=str, nargs='+', help='a satellite module name, leo...[...]')
parser.add_argument("output_dir", help="Directory where resulting plot will be saved.")

args = parser.parse_args()
csv_path = args.csv_path
sat_mods = args.sat_mods
output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"
csv_fname = csv_path.split("/")[-1]
# [1:-1] removes constellation prefix and _distances.csv suffix
output_path_template = output_dir + "_".join(csv_fname.split("_")[1:-1])

with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter=",")
    
    header = row_reader.__next__()
    # get sim second range
    start_sec = int(header[1])
    end_sec = int(header[-1])
    sec_range = range(start_sec, end_sec + 1)

    for row in row_reader:
        # positional_differences.py already shortens module name to leo.*[.*] part
        if row[0] in sat_mods:
            mod_leoname = row[0]
            diff_nums = [float(d) for d in row[1:]]
            rounded_diffs = [round(d, ndigits=2) for d in diff_nums]
            plt.plot(sec_range, rounded_diffs)
            plt.ylabel("difference")
            plt.xlabel("simulation second")
            
            plt.savefig(f'{output_path_template}_{mod_leoname}_distances.png', transparent=False, dpi=80, bbox_inches='tight')
            plt.clf()
            
            sat_mods.remove(row[0])
            if len(sat_mods) == 0:
                break