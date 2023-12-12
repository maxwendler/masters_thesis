import argparse
import csv
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_const_comm_periods",
                                 description="""Plots communication periods of all satellite modules of a constellation over the simulation time
                                                as lines with arbitrary y-value that is not 0 for each communication period.""")
parser.add_argument("all_periods_csv")
parser.add_argument("measurments_start_time", type=int)
parser.add_argument("sim_time_limit", type=int)
parser.add_argument("output_path")
args = parser.parse_args()

fig = go.Figure()
fig.update_layout(showlegend=False)
fig.update_xaxes(title_text="sim. second")

sec_range = list(range(args.measurments_start_time, args.sim_time_limit + 1))

average_pixel_width_per_char = 0.01

with open(args.all_periods_csv, "r") as csv_f:

    row_reader = csv.reader(csv_f)
    header = row_reader.__next__()

    for row in row_reader:
        
        modname = row[0]
        period_start_sec = int(row[1])
        period_end_sec = int(row[2])
        
        y_val = 1 

        # e.g. 15 to 20: seconds 15,16,17,18,19
        mod_vals = [0] * (period_start_sec - args.measurments_start_time)
        # e.g. 20 to 22: 20, 21, 22
        mod_vals += [y_val] * (period_end_sec - period_start_sec + 1)
        # e.g. 23 to 25: 23, 24, 25
        mod_vals += [0] * (args.sim_time_limit - period_end_sec)

        fig.add_trace(
            go.Scatter(x=sec_range, 
                    y=mod_vals
            )
        )

        annot_yshift = - (len(modname) * average_pixel_width_per_char / 2)
        fig.add_annotation(
            dict(
                font=dict(color="black",size=1),
                x=period_start_sec,
                y=annot_yshift,
                text=modname,
                textangle=90,
                showarrow=False
            )
        )


fig.write_image(args.output_path, width=1920, height=300)