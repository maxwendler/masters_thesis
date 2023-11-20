from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import argparse
import csv

parser = argparse.ArgumentParser(prog="plot_differences_both.py", description="Plots the differences of specified satellite modules from specified CSV as line and ecdf plot.")

parser.add_argument("csv_path", help="Path of csv file with (distance SGP4/Kepler at sim. second) vectors per satellite module.")
parser.add_argument('sat_mods', metavar='leo_modname', type=str, nargs='+', help='a satellite module name, leo...[...]')
parser.add_argument("output_path", help="Directory where resulting plot will be saved.")

args = parser.parse_args()
csv_path = args.csv_path
sat_mods = args.sat_mods
# output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"
csv_fname = csv_path.split("/")[-1]
# [1:-1] removes constellation prefix and _distances.csv suffix
# output_path_template = output_dir + "_".join(csv_fname.split("_")[1:-1])

fig = make_subplots(rows=1, cols=2, subplot_titles=("difference in km / sim sec.", "difference ecdf"))

with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter=",")
    
    header = row_reader.__next__()
    # get sim second range
    start_sec = int(header[1])
    end_sec = int(header[-1])
    sec_range = list(range(start_sec, end_sec + 1))

    for row in row_reader:
        # positional_differences.py already shortens module name to leo.*[.*] part
        if row[0] in sat_mods:
            mod_leoname = row[0]
            differences = [float(d) for d in row[1:]]
            differences_dict_ecdf = {"differences": differences}
            differences_dict_scatter = {"simulation_second": sec_range, "pos_difference_km": differences}

            fig.add_trace(
                go.Scatter(x=differences_dict_scatter["simulation_second"], y=differences_dict_scatter["pos_difference_km"]),
                row=1, col=1
            )

            ecdf = px.ecdf(differences_dict_ecdf, x="differences")
            fig.add_trace(ecdf.data[0], row=1, col=2)

            #fig.write_image(f'{output_path_template}_{mod_leoname}_distances_both.png')
            fig.write_image(args.output_path)

            sat_mods.remove(mod_leoname)
            if len(sat_mods) == 0:
                break