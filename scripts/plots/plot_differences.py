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

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import argparse
import csv
import json

parser = argparse.ArgumentParser(prog="plot_differences.py", description="Plots the differences of specified satellite modules from specified CSV as line and ecdf plot.")

parser.add_argument("csv_path", help="Path of csv file with (distance SGP4/Kepler at sim. second) vectors per satellite module.")
parser.add_argument('leo_modname', help='A satellite module name.')
parser.add_argument('tle_times_path', help="Path of JSON with simulation start time and epoch times of TLEs in numpy's datetime64 format.")
parser.add_argument("output_path", help="Directory where resulting plot will be saved.")
parser.add_argument("--ecdf", action="store_true", help="If flag is set, ECDF plot is plotted as well in second column.")
parser.add_argument("--comparison_csv")

args = parser.parse_args()
csv_path = args.csv_path
tle_times = None
with open(args.tle_times_path, "r") as times_f:
    tle_times = json.load(times_f)

if args.ecdf:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("difference in km / sim sec.", "difference ecdf"))
else:
    fig = go.Figure()

comp_differences = []
with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter=",")
    
    header = row_reader.__next__()
    # get sim second range
    start_sec = int(header[1])
    end_sec = int(header[-1])
    sec_range = list(range(start_sec, end_sec + 1))

    row_idx = 1
    for row in row_reader:
        # positional_differences.py already shortens module name to leo.*[.*] part
        if row[0] == args.leo_modname:
            mod_leoname = row[0]
            differences = [float(d) for d in row[1:]]
            differences_dict_ecdf = {"differences": differences}

            if args.ecdf:
                fig.add_trace(
                    go.Scatter(x=sec_range, y=differences),
                    row=1, col=1
                )
                ecdf = px.ecdf(differences_dict_ecdf, x="differences")
                fig.add_trace(ecdf.data[0], row=1, col=2)

            else:

                if args.comparison_csv:
                    
                    fig.add_trace(
                        go.Scatter(x=sec_range, y=differences, name="kepler")
                    )

                    fig.update_yaxes(title_text="distance to SGP4 in km")

                    with open(args.comparison_csv) as comp_csv:
                        
                        comp_row_reader = csv.reader(comp_csv, delimiter=",")
                        comp_row = None
                        for i in range(row_idx + 1):
                            comp_row = comp_row_reader.__next__()
                        
                        comp_differences = [float(d) for d in comp_row[1:]]

                        fig.add_trace(
                            go.Scatter(x=sec_range, y=comp_differences, name="circular")
                        )
                
                else: 
                    fig.add_trace(
                        go.Scatter(x=sec_range, y=differences)
                    )

            # add start time marking
            offset_to_start_sec = tle_times["sat_times"][mod_leoname]["offset_to_start"]
            epoch_in_start_time_frame = offset_to_start_sec

            if args.ecdf:
                fig.add_shape(
                    type="line",
                    x0=epoch_in_start_time_frame, y0=min(differences + comp_differences), x1=epoch_in_start_time_frame, y1=max(differences + comp_differences),
                    line=dict(color="Red", width=1, dash="dash"),
                    row=1, col=1
                )
                fig.add_annotation(
                    x=epoch_in_start_time_frame, y=max(differences + comp_differences),
                    text="epoch of TLE",
                    showarrow=False,
                    font=dict(size=14, color="Red"),
                    row=1, col=1
                )
            else:
                fig.add_shape(
                    type="line",
                    x0=epoch_in_start_time_frame, y0=min(differences + comp_differences), x1=epoch_in_start_time_frame, y1=max(differences + comp_differences),
                    line=dict(color="Red", width=1, dash="dash")
                )
                fig.add_annotation(
                    x=epoch_in_start_time_frame, y=max(differences + comp_differences),
                    text="epoch of TLE",
                    showarrow=False,
                    font=dict(size=14, color="Red")
                )
                fig.update_yaxes(title_text="distance to SGP4 in km")
            fig.write_image(args.output_path)

        row_idx += 1