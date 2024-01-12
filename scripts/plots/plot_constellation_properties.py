import argparse
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.keplertraces.tleparse import read
import plotly.graph_objects as go
import csv

parser = argparse.ArgumentParser()
parser.add_argument("tles_dir")
parser.add_argument("avg_alts_dir")
parser.add_argument("output_dir")
args = parser.parse_args()

tles_dir = args.tles_dir if args.tles_dir.endswith("/") else args.tles_dir + "/"
avg_alts_dir = args.avg_alts_dir if args.avg_alts_dir.endswith("/") else args.avg_alts_dir + "/"
output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"

tles_paths = [tles_dir + fname for fname in filter( lambda fname: not fname.endswith("_times.json") , os.listdir(tles_dir))]
constellation_compositions = constellation_compositions = { "starlink": ["starlink1", "starlink2", "starlink3", "starlink4"],
                              "iridiumNEXT": ["iridiumNEXT"],
                              "eccentric": ["eccentric"],
                              "oneweb": ["oneweb"],
                              "satnogs": ["satnogs"] }

constellation_tles_paths = {}
for constellation in constellation_compositions.keys():
    tle_files_prefixes = constellation_compositions[constellation]
    current_const_tles_paths = []
    for p in tles_paths:
        for prefix in tle_files_prefixes:
            if prefix in p:
                current_const_tles_paths.append(p)
    constellation_tles_paths[constellation] = current_const_tles_paths

all_tles_incs = []
all_tles_eccs = []
all_tles_meanmotions = []
all_tles_categories = []

for constellation in constellation_tles_paths.keys():
    current_tles_paths = constellation_tles_paths[constellation]
    tles = []
    for tles_path in current_tles_paths:
        tles += read(tles_path)

    tles_idxs = list(range(1, len(tles) + 1))
    tles_categories = [1] * len(tles)
    inclinations = sorted([tle.inc for tle in tles])
    eccs = sorted([tle.ecc for tle in tles])
    meanmotions = sorted([tle.n for tle in tles])

    os.makedirs(output_dir + constellation, exist_ok=True)

    # inclination figures
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=inclinations, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="inclination in °")
    line_fig.write_image(output_dir + constellation + "/" + "inclinations_line.svg")

    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=inclinations, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="inclination in °")
    vertical_fig.write_image(output_dir + constellation + "/" + "inclinations_vertical.svg")

    # eccentricity figures
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=eccs, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="eccentricity")
    line_fig.write_image(output_dir + constellation + "/" + "eccentricities_line.svg")

    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=eccs, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="eccentricity")
    vertical_fig.write_image(output_dir + constellation + "/" + "eccentricities_vertical.svg")

    # mean motion figures
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=meanmotions, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="mean motion in rev/day")
    line_fig.write_image(output_dir + constellation + "/" + "meanmotions_line.svg")

    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=meanmotions, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="mean motion in rev/day")
    vertical_fig.write_image(output_dir + constellation + "/" + "meanmotions_vertical.svg")

    all_tles_incs += inclinations
    all_tles_eccs += eccs
    all_tles_meanmotions += meanmotions
    all_tles_categories += [constellation] * len(inclinations)

# all constellations in one figs
# inclinations
all_const_fig = go.Figure(data=go.Scatter(x=all_tles_categories, y=all_tles_incs, mode='markers'))
all_const_fig.update_layout(title="all constellations")
all_const_fig.update_yaxes(title="inclination in °")
all_const_fig.write_image(output_dir + "all_inclinations.svg")

# eccentricities
all_const_fig = go.Figure(data=go.Scatter(x=all_tles_categories, y=all_tles_eccs, mode='markers'))
all_const_fig.update_layout(title="all constellations")
all_const_fig.update_yaxes(title="eccentricity")
all_const_fig.write_image(output_dir + "all_eccentricities.svg")

# mean motions
all_const_fig = go.Figure(data=go.Scatter(x=all_tles_categories, y=all_tles_meanmotions, mode='markers'))
all_const_fig.update_layout(title="all constellations")
all_const_fig.update_yaxes(title="mean motion in rev/day")
all_const_fig.write_image(output_dir + "all_meanmotions.svg")

# average altitudes separately as not from tles
all_tles_avg_alts = []
all_tles_avg_alts_categories = []

all_avg_alt_paths = [ avg_alts_dir + fname for fname in os.listdir(avg_alts_dir)]

for constellation in constellation_compositions.keys():
    constellation_components = constellation_compositions[constellation]
    const_avg_alt_paths = []
    for p in all_avg_alt_paths:
        for comp in constellation_components:
            if comp in p:
                const_avg_alt_paths.append(p)
    
    const_avg_alts = []
    for p in const_avg_alt_paths:

        with open(p, "r") as csv_f:

            row_reader = csv.reader(csv_f)
            header = row_reader.__next__()
            for row in row_reader:
                const_avg_alts.append(float(row[1]))
    
    const_avg_alts.sort()
    tles_idxs = list(range(1, len(const_avg_alts) + 1))
    
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=const_avg_alts, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="avg. altitude in km")
    line_fig.write_image(output_dir + constellation + "/" + "avg_alts_line.svg")

    tles_categories = [1] * len(const_avg_alts)
    
    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=const_avg_alts, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="avg. altitude in km")
    vertical_fig.write_image(output_dir + constellation + "/" + "avg_alts_vertical.svg")

    all_tles_avg_alts += const_avg_alts
    all_tles_avg_alts_categories += [constellation] * len(const_avg_alts)

all_avg_alts_fig = go.Figure(data=go.Scatter(x=all_tles_avg_alts_categories, y=all_tles_avg_alts, mode='markers'))
all_avg_alts_fig.update_layout(title="all constellations")
all_avg_alts_fig.update_yaxes(title="avg. altitude in km")
all_avg_alts_fig.write_image(output_dir + "all_avg_alts.svg")