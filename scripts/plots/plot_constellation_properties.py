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
import os, sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.keplertraces.tleparse import read
from scripts.utility.satname_to_modname import satname_to_modname
import plotly.graph_objects as go
import csv
from math import pi

parser = argparse.ArgumentParser()
parser.add_argument("tles_dir")
parser.add_argument("avg_radii_dir")
parser.add_argument("output_dir")
args = parser.parse_args()

tles_dir = args.tles_dir if args.tles_dir.endswith("/") else args.tles_dir + "/"
avg_radii_dir = args.avg_radii_dir if args.avg_radii_dir.endswith("/") else args.avg_radii_dir + "/"
output_dir = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"

constellation_tles_paths = {
    "IridiumNEXT": "../../examples/space_veins/tles/iridiumNEXT_2023-10-22-15-22-02.txt",
    "Starlink": "../../examples/space_veins/tles/avg_epoch_timestamps/undecomposed/starlink_2023-10-22-21-18-24.txt",
    "OneWeb": "../../ma-max-wendler/examples/space_veins/tles/avg_epoch_timestamps/undecomposed/oneweb_2023-10-22-22-28-26.txt",
    "SatNOGS": "../../ma-max-wendler/examples/space_veins/tles/satnogs_2023-10-22-20-54-21.txt",
    "Eccentric": "../../ma-max-wendler/examples/space_veins/tles/eccentric_2023-10-22-15-30-23.txt",
}
 
all_tles_incs = []
all_tles_eccs = []
all_tles_meanmotions = []
const_meanmotion_dicts = {}
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
    
    meanmotions_dict = {}
    for tle in tles:
        meanmotions_dict[tle.name] = tle.n
    const_meanmotion_dicts[constellation] = meanmotions_dict
    meanmotions_list = sorted(list(meanmotions_dict.values()))

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
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=meanmotions_list, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="mean motion in rev/day")
    line_fig.write_image(output_dir + constellation + "/" + "meanmotions_line.svg")

    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=meanmotions_list, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="mean motion in rev/day")
    vertical_fig.write_image(output_dir + constellation + "/" + "meanmotions_vertical.svg")

    all_tles_incs += inclinations
    all_tles_eccs += eccs
    all_tles_meanmotions += meanmotions_list
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

# can be uncommented when average radii files actually exist
"""
# average radii separately as not from tles
all_tles_avg_radii = []
all_tles_avg_radii_categories = []
all_tles_approx_velocities = []

all_avg_radii_paths = [ avg_radii_dir + fname for fname in os.listdir(avg_radii_dir)]

for constellation in constellation_compositions.keys():
    constellation_components = constellation_compositions[constellation]
    const_avg_radii_paths = []
    for p in all_avg_radii_paths:
        for comp in constellation_components:
            if comp in p:
                const_avg_radii_paths.append(p)
    
    const_avg_radii_dict = {}
    for p in const_avg_radii_paths:

        with open(p, "r") as csv_f:

            row_reader = csv.reader(csv_f)
            header = row_reader.__next__()
            for row in row_reader:
                const_avg_radii_dict[row[0]] = float(row[1])
    
    const_avg_radii_list = list(const_avg_radii_dict.values())
    const_avg_radii_list.sort()
    tles_idxs = list(range(1, len(const_avg_radii_list) + 1))
    
    line_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=const_avg_radii_list, mode='markers'))
    line_fig.update_layout(title=constellation)
    line_fig.update_yaxes(title="avg. radius in km")
    line_fig.write_image(output_dir + constellation + "/" + "avg_radii_line.svg")

    tles_categories = [1] * len(const_avg_radii_list)
    
    vertical_fig = go.Figure(data=go.Scatter(x=tles_categories, y=const_avg_radii_list, mode='markers'))
    vertical_fig.update_layout(title=constellation)
    vertical_fig.update_yaxes(title="avg. radius in km")
    vertical_fig.write_image(output_dir + constellation + "/" + "avg_radii_vertical.svg")
    
    ## plot mean motions at avg. radiuss
    # create satname, avg. radius, mean motion tuples
    meanmotions_dict = const_meanmotion_dicts[constellation]
    data_tuples = []

    for satname in meanmotions_dict.keys():
        meanmotion = meanmotions_dict[satname]
        modname = satname_to_modname(satname)
        avg_radius = const_avg_radii_dict[modname]
        data_tuples.append(tuple([satname, avg_radius, meanmotion]))
    
    # sort by average radius
    data_tuples.sort(key=lambda tuple: tuple[1])
    avg_radii = [tup[1] for tup in data_tuples]
    meanmotions = [tup[2] for tup in data_tuples]

    meanmotion_at_radius_fig = go.Figure(data=go.Scatter(x=avg_radii, y=meanmotions, mode="markers"))
    meanmotion_at_radius_fig.update_layout(title=constellation)
    meanmotion_at_radius_fig.update_xaxes(title="avg. radius in km")
    meanmotion_at_radius_fig.update_yaxes(title="mean motion in rev/day")
    meanmotion_at_radius_fig.write_image(output_dir + constellation + "/" + "meanmotion_at_avg_radius.svg")

    # plot approximate velocities
    velocities = []
    for data_tuple in data_tuples:
        circumference = 2 * pi * data_tuple[1]
        velocity_km_per_day = circumference * data_tuple[2]
        velocities.append(velocity_km_per_day)
    
    velocities_fig = go.Figure(data=go.Scatter(x=tles_idxs, y=velocities, mode="markers"))
    velocities_fig.update_layout(title=constellation)
    velocities_fig.update_yaxes(title="approx. velocity in km/day")
    velocities_fig.write_image(output_dir + constellation + "/" + "approx_velocities.svg")

    all_tles_approx_velocities += velocities
    all_tles_avg_radii += const_avg_radii_list
    all_tles_avg_radii_categories += [constellation] * len(const_avg_radii_list)

all_avg_radii_fig = go.Figure(data=go.Scatter(x=all_tles_avg_radii_categories, y=all_tles_avg_radii, mode='markers'))
all_avg_radii_fig.update_layout(title="all constellations")
all_avg_radii_fig.update_yaxes(title="avg. radius in km")
all_avg_radii_fig.write_image(output_dir + "all_avg_radii.svg")

all_approx_velocities_fig = go.Figure(data=go.Scatter(x=all_tles_avg_radii_categories, y=all_tles_approx_velocities, mode='markers'))
all_approx_velocities_fig.update_layout(title=constellation)
all_approx_velocities_fig.update_yaxes(title="approx. velocity in km/day")
all_approx_velocities_fig.write_image(output_dir + "all_approx_velocities.svg")

"""