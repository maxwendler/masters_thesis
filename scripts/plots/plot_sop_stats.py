"""
Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

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
parser.add_argument("--angles_csv_paths", required=True, nargs=2, help="Paths of elevation angles of both mobilities.")
parser.add_argument("--distances_csv_paths", required=True, nargs=2, help="Paths of distances of both mobilities.")
parser.add_argument("--delays_csv_paths", required=True, nargs=2, help="Paths of delays of both mobilities.")
parser.add_argument("output_base_path")
parser.add_argument("--formats", choices=["svg","html"], nargs="+")
parser.add_argument("--min_angle", type=float, help="Minimum elevation angle for which horizontal line is plotted in elevation angles plots.")
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
# add mobility name annotations for both columns
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

# add annotation for used TLE's epoch's offset to simulation start time in seconds
tle_times = None
if args.tle_times_path:
    with open(args.tle_times_path, "r") as times_f:
        tle_times = json.load(times_f)
        offset_to_start_time_days = float(tle_times["sat_times"][args.leo_modname]["offset_to_start"])
        offset_to_start_sec = offset_to_start_time_days * 43200

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

# columns 1 and 2 for both mobilities
for col_idx in range(1, 3):
    plot_row_idx = 1
    csvs_idx = col_idx - 1

    communication_periods = None
    
    # plot elevation angles
    with open(args.angles_csv_paths[csvs_idx], "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()
        sim_second_range = parse_second_range_from_header(header)
    
        for row in row_reader:
            if row[0] == args.leo_modname:
                angles = [float(a) for a in row[1:]]

                fig.add_trace(
                    go.Scatter(x=sim_second_range, y=angles),
                    row=plot_row_idx, col=col_idx
                )

                # add annotations for start, end and duration of each communication period
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

                        # calc y position of whole layout
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
    
    # plot distances
    with open(args.distances_csv_paths[csvs_idx], "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()

        for row in row_reader:
            if row[0] == args.leo_modname:
                
                distances = [float(d) for d in row[1:]]
                
                fig.add_trace(
                    go.Scatter(x=sim_second_range, y=distances),
                    row=plot_row_idx, col=col_idx
                )
                
                plot_row_idx += 1
                break
    
    # plot delays
    with open(args.delays_csv_paths[csvs_idx], "r") as csv_f:
        
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()

        for row in row_reader:
            if row[0] == args.leo_modname:
                
                delays = [float(d) for d in row[1:]]
                
                fig.add_trace(
                    go.Scatter(x=sim_second_range, y=delays),
                    row=plot_row_idx, col=col_idx
                )
                
                plot_row_idx += 1
                break

# add horizontal line of minimum elevation angle to elevation angles plots
if args.min_angle:
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

    # do not use as subplots shall line up, looking for alternative solution
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