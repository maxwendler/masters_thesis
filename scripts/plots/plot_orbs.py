import argparse
from parse_coords_file import parse_coords_file
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import re
import numpy as np
from math import inf

parser = argparse.ArgumentParser(prog="plot_orbs.py", 
                                 description="""Plots the orbits from the given coordinate CSVs and trace files using cartesian coordinates. 
                                            At least one coordinate CSV is required to determine the start second of coordinate recording, i.e. 
                                            first entry to be used from a trace file.""")

parser.add_argument('-c', '--csv_paths', metavar='csv_path', type=str, nargs='+', required=True, help='One or more paths of a CSV with cartesian coordinate list of *one* satellite module.')
parser.add_argument('-t', '--trace_paths', metavar='trace_path', type=str, nargs='*', help="Any number of paths of a trace with cartesian coordinate list of *one* satellite.")
parser.add_argument('-o', '--output_path', metavar='output_path', type=str, required=True, help="Path where plot of orbits will be saved.")
parser.add_argument('-e', "--earth", action="store_true", help="If flag is set, also plots sphere with average earth radius.")

args = parser.parse_args()
csv_paths = args.csv_paths
trace_paths = args.trace_paths

modname_re = r"leo.*]"

# color cycle of length ten
color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
color_idx = 0

layout = go.Layout(
    title='3D Line Plots in Plotly',
    #aspectratio = dict( x=1, y=1, z=1 ),
    xaxis=dict(title='X'),
    yaxis=dict(title='Y'),
    # zaxis=dict(title='Z')
)

fig = go.Figure(layout=layout)

if args.earth:
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    xs = 6371 * np.outer(np.cos(u), np.sin(v))
    ys = 6371 * np.outer(np.sin(u), np.sin(v))
    zs = 6371 * np.outer(np.ones(np.size(u)), np.cos(v))

    colorscale = [[0, 'gray'], [1, 'gray']]
    fig.add_surface(x=xs, y=ys, z=zs, colorscale=colorscale, showscale=False)

start_second = None
start_second_src = None
coords_len = None
coords_len_src = None

min_z = inf
max_z = -inf

for csv_p in csv_paths:
    
    coords, csv_start_second = parse_coords_file(csv_p, "csv")
    
    if not start_second:
        start_second = csv_start_second
        start_second_src = csv_p
    else:
        if start_second != csv_start_second:
            error_str = f"Mismatch between start second of {start_second_src} and {csv_p}!"
            raise ValueError(error_str)

    if not coords_len:
        print("set coords_len")
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

    orb_line = go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=leo_modname, line=dict(
            color=color_cycle[color_idx % len(color_cycle)]
        )
    )
    
    orb_start = go.Scatter3d(x=xs[:1], y=ys[:1], z=zs[:1], mode='markers', showlegend=False, line=dict(
            color=color_cycle[color_idx % len(color_cycle)]
        )
    )
    
    color_idx += 1

    fig.add_trace(orb_start)
    fig.add_trace(orb_line)

for trace_p in trace_paths:

    coords = parse_coords_file(trace_p, "trace")[(start_second - 1):]

    if coords_len != len(coords):
        error_str = f"Mismatch of number of coordinates of {coords_len_src} ({coords_len}) and {trace_p} ({len(coords)})!"
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

    satname = trace_p.split("/")[-1].removesuffix(".trace")

    orb_line = go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=satname, line=dict(
            color=color_cycle[color_idx % len(color_cycle)]
        )
    )
    
    orb_start = go.Scatter3d(x=xs[:1], y=ys[:1], z=zs[:1], mode='markers', showlegend=False, line=dict(
            color=color_cycle[color_idx % len(color_cycle)]
        )
    )
    
    color_idx += 1

    fig.add_trace(orb_start)
    fig.add_trace(orb_line)

max_z += 500
min_z -= 500

z_0 = go.Scatter3d(x=[0, 0], y=[0, 0], z=[min_z, max_z], mode='lines', showlegend=False, line=dict(
            color="black", dash="dash"
        )
    )

fig.add_trace(z_0)

fig.show()