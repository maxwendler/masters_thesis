import argparse
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import re
import numpy as np
from math import inf
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.parse_csvs import parse_coords_csv_to_list

parser = argparse.ArgumentParser(prog="plot_orbs.py", 
                                 description="""Plots the orbits from the given coordinate CSVs using cartesian coordinates.""")

parser.add_argument('-c', '--csv_paths', metavar='csv_path', type=str, nargs='*', help='One or more paths of a CSV with cartesian coordinate list of *one* satellite module.')
parser.add_argument('-o', '--output_path', metavar='output_path', type=str, required=True, help="Path where plot of orbits will be saved.")
parser.add_argument('-e', "--earth", action="store_true", help="If flag is set, also plots sphere with average earth radius.")

args = parser.parse_args()

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

        orb_max_z = max(zs)
        orb_min_z = min(zs)
        if orb_max_z > max_z:
            max_z = orb_max_z
        if orb_min_z < min_z:
            min_z = orb_min_z

        leo_modname = re.search(modname_re, csv_p).group()

        color = color_cycle[color_idx % len(color_cycle)]

        orb_line = go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=leo_modname, line=dict(
                color=color
            )
        )
        
        orb_start = go.Scatter3d(x=xs[:1], y=ys[:1], z=zs[:1], mode='markers', name=leo_modname + "_start", line=dict(
                color=color
            )
        )
        
        color_idx += 1

        fig.add_trace(orb_start)
        fig.add_trace(orb_line)

# start second was not set because no csv paths are used, so just read traces from first entry
if not start_second:
    start_second = 1

max_z += 500
min_z -= 500

# plot polar axis
z_0 = go.Scatter3d(x=[0, 0], y=[0, 0], z=[min_z, max_z], mode='lines', showlegend=False, line=dict(
            color="black", dash="dash"
        )
    )

fig.add_trace(z_0)
fig.write_html(args.output_path)