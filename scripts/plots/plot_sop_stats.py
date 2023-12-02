import argparse
import csv
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import sys, os
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.statistics.comm_period_info import get_communication_periods


def parse_second_range_from_header(header: str):
    start_second = int(header[1])
    end_second = int(header[-1])
    return list(range(start_second, end_second + 1))

parser = argparse.ArgumentParser(prog="plot_sop_stat.py", description="Plots at least one of elevation angle, distance and propagation delay relative to SOP from given CSV files.")
parser.add_argument("leo_modname")
parser.add_argument("--angles_csv_paths", nargs=2)
parser.add_argument("--distances_csv_paths", nargs=2)
parser.add_argument("--delays_csv_paths", nargs=2)
parser.add_argument("output_base_path")
parser.add_argument("--formats", choices=["svg","html"], nargs="+")
parser.add_argument("--min_angle", type=float)
parser.add_argument("--tle_times_path")
args = parser.parse_args()
formats = args.formats

if not args.angles_csv_paths and not args.distances_csv_paths and args.delays_csv_paths:
    raise ValueError("At least two csv paths of a metric are required!")

row_num = 0
subplot_titles = []
if args.angles_csv_paths:
    row_num += 1
    subplot_titles.append("elevation angle in ° to SOP at sim. second")
    subplot_titles.append("elevation angle in ° to SOP at sim. second")
if args.distances_csv_paths:
    row_num += 1
    subplot_titles.append("distance in km to SOP at sim. second")
    subplot_titles.append("distance in km to SOP at sim. second")
if args.delays_csv_paths:
    row_num += 1
    subplot_titles.append("delay in ms from SOP to sat. at sim. second")
    subplot_titles.append("delay in ms from SOP to sat. at sim. second")

fig = make_subplots(rows=row_num, cols=2, subplot_titles=subplot_titles)    

mobility_strs = args.output_base_path.split("/")[-1].split("_")[0].split("-")
fig.add_annotation(dict(font=dict(color="black",size=14),
                        x=0,
                        y=1.1,
                        showarrow=False,
                        text=f"{mobility_strs[0]} results",
                        textangle=0,
                        xref="paper",
                        yref="paper"))

fig.add_annotation(dict(font=dict(color="black",size=14),
                        x=0.6,
                        y=1.1,
                        showarrow=False,
                        text=f"{mobility_strs[1]} results",
                        textangle=0,
                        xref="paper",
                        yref="paper"))

tle_times = None
if args.tle_times_path:
    with open(args.tle_times_path, "r") as times_f:
        tle_times = json.load(times_f)
        offset_to_start_time_days = float(tle_times["sat_times"][args.leo_modname]["offset_to_start"])
        offset_to_start_sec = offset_to_start_time_days * 86400 

        y_pos = 1.05

        fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=0,
                            y=y_pos,
                            showarrow=False,
                            text=f"satellite epoch relative to start time: at {round(offset_to_start_sec, 1)} s",
                            textangle=0,
                            xref="paper",
                            yref="paper")
                        )

sim_second_range = None

for col_idx in range(1, 3):
    plot_row_idx = 1
    csvs_idx = col_idx - 1

    communication_periods = None
    if args.angles_csv_paths:
        
        with open(args.angles_csv_paths[csvs_idx], "r") as csv_f:
            
            row_reader = csv.reader(csv_f)
            header = row_reader.__next__()
            sim_second_range = parse_second_range_from_header(header)
        
            for row in row_reader:
                if row[0] == args.leo_modname:
                    angles = [float(a) for a in row[1:]]

                    angles_dict = {"sim. second": sim_second_range, "elevation angle in °": angles}
                    
                    fig.add_trace(
                        go.Scatter(x=angles_dict["sim. second"], y=angles_dict["elevation angle in °"]),
                        row=plot_row_idx, col=col_idx
                    )

                    if args.min_angle:
                        communication_periods = get_communication_periods(angles, args.min_angle, sim_second_range[0], 1)
                        print("Second periods when communication is possible:", communication_periods)

                        for p in communication_periods:
                            start_sec = p[0]
                            end_sec = p[1]
                            middle_sec = (start_sec + end_sec) / 2

                            fig.add_annotation(
                                x=middle_sec, y=130,
                                text=f"{start_sec}",
                                showarrow=False,
                                font=dict(size=8, color="Black"),
                                row=plot_row_idx, col=col_idx,
                                textangle=90
                            )

                            fig.add_annotation(
                                x=middle_sec, y=-120,
                                text=f"{end_sec}",
                                showarrow=False,
                                font=dict(size=8, color="Black"),
                                row=plot_row_idx, col=col_idx,
                                textangle=90
                            )

                            # calc y of whole layout
                            plot_bottom_y = 1 - (plot_row_idx / row_num) - 0.2

                            fig.add_annotation(
                                x=middle_sec, y=-200,
                                text=f"={end_sec - start_sec}",
                                showarrow=False,
                                font=dict(size=8, color="Black"),
                                xref="x"+str(col_idx),
                                yref="paper",
                                row=plot_row_idx, col=col_idx
                            )

                    plot_row_idx += 1
                    break

    if args.distances_csv_paths:
        
        with open(args.distances_csv_paths[csvs_idx], "r") as csv_f:
            
            row_reader = csv.reader(csv_f)
            header = row_reader.__next__()
            # header not parsed yet
            if not sim_second_range:
                sim_second_range = parse_second_range_from_header(header)

            for row in row_reader:
                if row[0] == args.leo_modname:
                    
                    distances = [float(d) for d in row[1:]]
                    dists_dict = {"sim. second": sim_second_range, "distance in km": distances}
                    
                    fig.add_trace(
                        go.Scatter(x=dists_dict["sim. second"], y=dists_dict["distance in km"]),
                        row=plot_row_idx, col=col_idx
                    )
                    
                    plot_row_idx += 1
                    break

    if args.delays_csv_paths:
        
        with open(args.delays_csv_paths[csvs_idx], "r") as csv_f:
            
            row_reader = csv.reader(csv_f)
            header = row_reader.__next__()
            # header not parsed yet
            if not sim_second_range:
                sim_second_range = parse_second_range_from_header(header)

            for row in row_reader:
                if row[0] == args.leo_modname:
                    
                    delays = [float(d) for d in row[1:]]
                    delays_dict = {"sim. second": sim_second_range, "delay in s": delays}
                    
                    fig.add_trace(
                        go.Scatter(x=delays_dict["sim. second"], y=delays_dict["delay in s"]),
                        row=plot_row_idx, col=col_idx
                    )
                    
                    plot_row_idx += 1
                    break

if args.min_angle and args.angles_csv_paths:
    fig.add_shape(
        type="line",
        x0=sim_second_range[0], y0=args.min_angle, x1=sim_second_range[-1], y1=args.min_angle,
        line=dict(color="Red", width=1, dash="dash"),
        row=1, col=1
    )

    fig.add_shape(
        type="line",
        x0=sim_second_range[0], y0=args.min_angle, x1=sim_second_range[-1], y1=args.min_angle,
        line=dict(color="Red", width=1, dash="dash"),
        row=1, col=2    
    )

    # do not use as subplots shall line up
    """
    fig.add_annotation(
        x=sim_second_range[0] + 1000, y=args.min_angle + 20,
        text="min. angle",
        showarrow=False,
        font=dict(size=10, color="Red"),
        row=1, col=1
    )
    """

if "svg" in formats:
    fig.write_image(args.output_base_path + ".svg", width=1920, height=1080)
if "html" in formats:
    fig.write_html(args.output_base_path + ".html")