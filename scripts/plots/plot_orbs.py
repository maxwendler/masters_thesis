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
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import re
import numpy as np
from math import inf
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_list
import json

parser = argparse.ArgumentParser(prog="plot_orbs.py", 
                                 description="""Plots the orbits from the given coordinate CSVs using cartesian coordinates.""")
parser.add_argument("tle_times")
parser.add_argument('-c', '--csv_paths', metavar='csv_path', type=str, nargs='*', help='One or more paths of a CSV with cartesian coordinate list of *one* satellite module.')
parser.add_argument('-o', '--output_path', metavar='output_path', type=str, required=True, help="Path where plot of orbits will be saved.")
parser.add_argument('-e', "--earth", action="store_true", help="If flag is set, also plots sphere with average earth radius.")

args = parser.parse_args()

with open(args.tle_times, "r") as json_f:
    tle_times = json.load(json_f)

output_dir = "/".join(args.output_path.split("/")[:-1])
os.makedirs(output_dir, exist_ok=True)

csv_paths = args.csv_paths

modname_re = r"leo.*]"

# color cycle of length ten
color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
color_idx = 0

# title with constellation / configuration (if one mobility) and coordinate frame
layout = go.Layout(
    title= " ".join(args.output_path.split("/")[-1].split("_")[:2])
)

fig = go.Figure(layout=layout)

# plot earth sphere
if args.earth:
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    xs = 6371 * np.outer(np.cos(u), np.sin(v))
    ys = 6371 * np.outer(np.sin(u), np.sin(v))
    zs = 6371 * np.outer(np.ones(np.size(u)), np.cos(v))

    colorscale = [[0, 'white'], [1, 'white']]
    fig.add_surface(x=xs, y=ys, z=zs, colorscale=colorscale, showscale=False)

start_second = None
start_second_src = None
coords_len = None
coords_len_src = None

# for getting z values to plot polar axis
min_z = inf
max_z = -inf

if csv_paths:
    # plot orbits of each satellite module
    for csv_p in csv_paths:

        fname = csv_p.split("/")[-1]
        constellation = fname.split("_")[0].split("-")[0]
        mobility = fname.split("_")[0].split("-")[1]
        
        coords, csv_start_second = parse_coords_csv_to_list(csv_p)
        
        if not start_second:
            start_second = csv_start_second
            start_second_src = csv_p
        else:
            if start_second != csv_start_second:
                error_str = f"Mismatch between start second of {start_second_src} and {csv_p}!"
                raise ValueError(error_str)

        if not coords_len:
            coords_len = len(coords)
            coords_len_src = csv_p
        else:
            if coords_len != len(coords):
                error_str = f"Mismatch of number of coordinates of {coords_len_src} ({coords_len}) and {csv_p} ({len(coords)})!"
                raise IndexError(error_str)

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        zs = [c[2] for c in coords]

        # for plotting polar axis
        orb_max_z = max(zs)
        orb_min_z = min(zs)
        if orb_max_z > max_z:
            max_z = orb_max_z
        if orb_min_z < min_z:
            min_z = orb_min_z

        leo_modname = re.search(modname_re, csv_p).group()

        color = color_cycle[color_idx % len(color_cycle)]
        
        # orbit
        orb_line = go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=f"{leo_modname} - {mobility}", line=dict(
                color=color
            )
        )
        
        # marker for position at simulation start
        orb_start = go.Scatter3d(x=xs[:1], y=ys[:1], z=zs[:1], mode='markers', name=f"{leo_modname} - {mobility} - start", line=dict(
                color=color
            )
        )

        mod_epoch_sec = int(float(tle_times["sat_times"][leo_modname]["offset_to_start"]))

        # marker for position at TLE epoch
        orb_epoch = go.Scatter3d(x=xs[mod_epoch_sec:mod_epoch_sec+1], y=ys[mod_epoch_sec:mod_epoch_sec+1], z=zs[mod_epoch_sec:mod_epoch_sec+1], mode='markers', name=f"{leo_modname} - {mobility} - epoch", line=dict(
                color=color
            )
        )
        
        color_idx += 1

        fig.add_trace(orb_start)
        fig.add_trace(orb_line)
        fig.add_trace(orb_epoch)

# start second was not set because no csv paths are used, so just read traces from first entry
if not start_second:
    start_second = 1

# plot polar axis
max_z += 500
min_z -= 500
z_0 = go.Scatter3d(x=[0, 0], y=[0, 0], z=[min_z, max_z], mode='lines', showlegend=False, line=dict(
            color="black", dash="dash"
        )
    )

fig.add_trace(z_0)
fig.write_html(args.output_path)