import argparse
import csv
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog="plot_differences.py", description="Plots the differences of specified satellite modules from specified CSV.")

parser.add_argument("csv_path", help="Path of csv file with (distance SGP4/Kepler at sim. second) vectors per satellite module.")
parser.add_argument('sat_mods', metavar='leo_modname', type=str, nargs='+', help='a satellite module name, leo...[...]')

args = parser.parse_args()
csv_path = args.csv_path
sat_mods = args.sat_mods

with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter=",")
    
    header = row_reader.__next__()
    print(header)
    # get sim second range
    start_sec = int(header[1])
    end_sec = int(header[-1])
    sec_range = range(start_sec, end_sec + 1)

    for row in row_reader:
        # positional_differences.py already shortens module name to leo.*[.*] part
        if row[0] in sat_mods:
            mod_leoname = row[0]
            dist_nums = [float(d) for d in row[1:]]
            rounded_dists = [round(d, ndigits=2) for d in dist_nums]
            plt.plot(sec_range, rounded_dists)
            plt.ylabel("difference")
            plt.xlabel("simulation second")
            
            plt.savefig(f'/workspaces/ma-max-wendler/scripts/plots/test_output/{mod_leoname}_{args.frame}_distances.png', transparent=False, dpi=80, bbox_inches='tight')
            plt.clf()
            