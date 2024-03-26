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
import json
import plotly.graph_objects as go

parser = argparse.ArgumentParser()
parser.add_argument("availables_diffs_json")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.availables_diffs_json, "r") as json_f:
    availables_diffs_dict = json.load(json_f)

availables_diffs = availables_diffs_dict["available_sat_diffs"]
measurement_start_time = availables_diffs[0]["sim_time"]
sim_time_limit = availables_diffs[-1]["sim_time"]

sim_times = list(range(measurement_start_time, sim_time_limit + 1))
available_num_diffs = [diff_dict["sat_num_diff"] for diff_dict in availables_diffs]

fig = go.Figure(data=go.Scatter(x=sim_times, y=available_num_diffs, mode='lines'))

fig.update_layout(title_text=f"avg. absolute sat. num. difference: {availables_diffs_dict['avg_abs_sat_num_diff']} <br>time with num. diff. to total: {availables_diffs_dict['time_with_num_diff_to_total_time']}")
fig.update_xaxes(title_text='simulation second')
fig.update_yaxes(title_text="difference in number of available satellites")

fig.write_image(args.output_path)