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
import plotly.express as px
import json

def parse_difference_csv(csv_path):
    """
    Parses each line of pos difference / distance in CSV into (1) list of module names and
    (2) list of list of distance values. 
    """
    with open(csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()

        modnames = []
        sat_distances = []

        for row in row_reader:
            # filter dimensional distances
            if not "_vector" in row[0]:
                modnames.append(row[0])
                distances = [ float(d) for d in row[1:] ]
                sat_distances.append(distances)
                
    return modnames, sat_distances

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="plot_difference_distributions", description="Plots sum histrogram of coordinate differences & difference box plot of each satellite.")
    parser.add_argument("difference_csv_path", help="Path of the csv of coordinate differences per satellite.")
    parser.add_argument("output_basepath", help="Directory where both plots will be saved.")
    args = parser.parse_args()

    difference_csv_path = args.difference_csv_path
    satnames, sat_distances = parse_difference_csv(difference_csv_path)

    sat_distsums = [sum(distances) for distances in sat_distances]
    avg_distsum = sum(sat_distsums) / len(sat_distsums)
    avg_dist = avg_distsum / len(sat_distances[0])

    # sum of distances histogram with horizontal line for avg distsum
    # subtitle: avg. dist
    fig = px.bar(x=satnames, y=sat_distsums, labels={'x': f'Average difference: {round(avg_dist, 6)} km', 'y': "difference sum in km"})
    fig.add_hline(y=avg_distsum, annotation={"text": "avg sum"})

    fig.write_image(args.output_basepath + "sum-histogram.svg")
    fig.write_html(args.output_basepath + "sum-histogram.html")
    
    # JSON output
    out_dict = {}
    out_dict["avg_diff_sum"] = avg_distsum
    out_dict["avg_diff"] = avg_dist
    out_dict["sats"] = {}
    for i in range(len(satnames)):
        out_dict["sats"][satnames[i]] = {
            "diff_sum": sat_distsums[i],
            "avg_diff": sat_distsums[i] / len(sat_distances[0])
        }

    with open(args.output_basepath + "avg_difference.json", "w") as avg_difference_f:
        json.dump(out_dict, avg_difference_f, indent=4)