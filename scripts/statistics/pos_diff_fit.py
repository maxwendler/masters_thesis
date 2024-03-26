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
import csv
from math import floor, inf
from numpy.polynomial import Polynomial

parser = argparse.ArgumentParser()
parser.add_argument("pos_diff_csv", help="CSV of between-model positional distances of a constellation.")
parser.add_argument("tle_times", help="Epoch times and epoch offsets to start of the satellite modules of a constellation.")
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.tle_times, "r") as times_json:
    tle_times = json.load(times_json)

satnum = len(tle_times["sat_times"])

# only use periods of backward / forward propagation longer than this line fit to reduce influence of periodicity
fit_period_len_limit = int(43205 * 2 / 8)

output_dict = {}
mod_fits_dict = {}
# before/after: w.r.t. to epoch
before_x_factors = []
after_x_factors = []
before_constants = []
after_constants = []
sat_counter = 0
diff_csv_fname = args.pos_diff_csv.split("/")[-1]

max_before_x_factor = -inf
max_before_x_factor_mod = None
min_before_x_factor = inf
min_before_x_factor_mod = None
max_after_x_factor = -inf
max_after_x_factor_mod = None
min_after_x_factor = inf
min_after_x_factor_mod = None

max_before_constant = -inf
max_before_constant_mod = None
min_before_constant = inf
min_before_constant_mod = None
max_after_constant = -inf
max_after_constant_mod = None
min_after_constant = inf
min_after_constant_mod = None

# lt/gt: x factor before epoch </> x factor after epoch
before_lt_percent = 0
before_gt_percent = 0
before_lt_before_avgs = []
before_lt_before_growths = []
before_lt_after_growths = []
before_lt_after_avgs = []
before_gt_before_growths = []
before_gt_before_avgs = []
before_gt_after_growths = []
before_gt_after_avgs = []

with open(args.pos_diff_csv, "r") as diff_csv:
    row_reader = csv.reader(diff_csv)
    header = row_reader.__next__()

    # calculate for each satellite module of constellation
    for row in row_reader:
        mod_dict = {}
        modname = row[0]
        mod_diffs = [float(diff) for diff in row[1:]]
        epoch_sec = int(float(tle_times["sat_times"][modname]["offset_to_start"])) 

        before_avg_diff = None
        after_avg_diff = None

        mod_secs_after_epoch = 0
        mod_secs_before_epoch = 0

        # start before epoch
        if epoch_sec > 0:
            if epoch_sec < 43205:
                mod_secs_before_epoch = epoch_sec
            else:
                mod_secs_before_epoch = 43205
            mod_secs_after_epoch = 43205 - mod_secs_before_epoch
        # start after epoch
        else:
            mod_secs_before_epoch = 0
            mod_secs_after_epoch = 43205

        # skip if backward and forward propagation periods not long enough
        # ensures that backward/forward propagation periods actually touch epoch
        if not (mod_secs_before_epoch >= fit_period_len_limit and mod_secs_after_epoch >= fit_period_len_limit):
            continue

        # backward line fit
        before_x = None
        if mod_secs_before_epoch > 1 :
            indices = list(range(mod_secs_before_epoch + 1))
            # reversed: fit in backward direction from epoch
            before_diffs = list(reversed(mod_diffs[:(mod_secs_before_epoch+1)]))
            
            diffs_for_avg = before_diffs[:fit_period_len_limit + 1]
            before_avg_diff = sum(diffs_for_avg) / len(diffs_for_avg)
            
            fun = Polynomial.fit(indices, before_diffs, deg=1)
            coef = fun.convert().coef
            before_x = coef[1]
            before_constants.append(coef[0])
            before_x_factors.append(coef[1])
            if coef[1] > max_before_x_factor:
                max_before_x_factor = coef[1]
                max_before_x_factor_mod = modname
            if coef[1] < min_before_x_factor:
                min_before_x_factor = coef[1]
                min_before_x_factor_mod = modname
            if coef[0] > max_before_constant:
                max_before_constant = coef[0]
                max_before_constant_mod = modname
            if coef[0] < min_before_constant:
                min_before_constant = coef[0]
                min_before_constant_mod = modname
            mod_dict["before_fit"] = {
                "y_shift": coef[0],
                "growth": coef[1] 
            }

        # forward line fit
        after_x = None
        if mod_secs_after_epoch > 1:
            
            diff_idx_offset = 0
            if epoch_sec >= 0:
                diff_idx_offset = epoch_sec
            else:
                diff_idx_offset = 0

            indices = list(range(mod_secs_after_epoch + 1))
            after_diffs = mod_diffs[diff_idx_offset:(diff_idx_offset + mod_secs_after_epoch+1)]
            diffs_for_avg = after_diffs[:fit_period_len_limit + 1]
            after_avg_diff = sum(diffs_for_avg) / len(diffs_for_avg)
            fun = Polynomial.fit(indices, after_diffs, deg=1)
            coef = fun.convert().coef
            after_x = coef[1]
            after_constants.append(coef[0])
            after_x_factors.append(coef[1])
            if coef[1] > max_after_x_factor:
                max_after_x_factor = coef[1]
                max_after_x_factor_mod = modname
            if coef[1] < min_after_x_factor:
                min_after_x_factor = coef[1]
                min_after_x_factor_mod = modname
            if coef[0] > max_after_constant:
                max_after_constant = coef[0]
                max_after_consatnt_mod = modname
            if coef[0] < min_after_constant:
                min_after_constant = coef[0]
                min_after_constant_mod = modname
            mod_dict["after_fit"] = {
                "y_shift": coef[0],
                "growth": coef[1] 
            }
        
        if before_avg_diff < after_avg_diff:
            before_lt_before_avgs.append(before_avg_diff)
            before_lt_after_avgs.append(after_avg_diff)
            before_lt_before_growths.append(before_x)
            before_lt_after_growths.append(after_x)
        else:
            before_gt_before_avgs.append(before_avg_diff)
            before_gt_after_avgs.append(after_avg_diff)
            before_gt_before_growths.append(before_x)
            before_gt_after_growths.append(after_x)


        mod_dict["before_diff_avg"] = before_avg_diff
        mod_dict["after_diff_avg"] = after_avg_diff
        mod_fits_dict[modname] = mod_dict
        
        sat_counter += 1 
        print(f"{diff_csv_fname}: {sat_counter}/{satnum}")

if len(before_x_factors) > 0:
    output_dict["before_y_avg"] = sum(before_constants)/len(before_constants)
    output_dict["before_x_avg"] = sum(before_x_factors)/len(before_x_factors)

if len(after_x_factors) > 0:
    output_dict["after_y_avg"] = sum(after_constants)/len(after_constants)
    output_dict["after_x_avg"] = sum(after_x_factors)/len(after_x_factors)

# calculate ratios of relations between backward and forward propagation periods and calculate average between-model distances in these periods
before_lt_percent = len(before_lt_before_growths) / (len(before_lt_before_growths) + len(before_gt_before_growths))
before_lt_before_avg = None
before_lt_after_avg = None
before_lt_avg_before_growth = None
before_lt_avg_after_growth = None
if len(before_lt_before_avgs) > 0:
    before_lt_before_avg = sum(before_lt_before_avgs) / len(before_lt_before_avgs)
    before_lt_after_avg = sum(before_lt_after_avgs) / len(before_lt_after_avgs)
    before_lt_avg_before_growth = sum(before_lt_before_growths) / len(before_lt_before_growths)
    before_lt_avg_after_growth = sum(before_lt_after_growths) / len(before_lt_after_growths)
before_gt_percent = len(before_gt_before_growths) / (len(before_lt_before_growths) + len(before_gt_before_growths))
before_gt_before_avg = None
before_gt_after_avg = None
before_gt_avg_before_growth = None
before_gt_avg_after_growth = None
if len(before_gt_before_avgs) > 0:
    before_gt_before_avg = sum(before_gt_before_avgs) / len(before_gt_before_avgs)
    before_gt_after_avg = sum(before_gt_after_avgs) / len(before_gt_after_avgs)
    before_gt_avg_before_growth = sum(before_gt_before_growths) / len(before_gt_before_growths)
    before_gt_avg_after_growth = sum(before_gt_after_growths) / len(before_gt_after_growths)

before_lt_gt_dict = {
    "before_lt_percent": before_lt_percent,
    "before_lt_before_avg":before_lt_before_avg,
    "before_lt_after_avg":before_lt_after_avg,
    "before_lt_avg_before_growth":before_lt_avg_before_growth,
    "before_lt_avg_after_growth":before_lt_avg_after_growth,
    "before_gt_percent":before_gt_percent,
    "before_gt_before_avg":before_gt_before_avg,
    "before_gt_after_avg": before_gt_after_avg,
    "before_gt_avg_before_growth":before_gt_avg_before_growth,
    "before_gt_avg_after_growth":before_gt_avg_after_growth
}
output_dict["before_lt_gt"] = before_lt_gt_dict
output_dict["max_min"] = {
    "max_before_x": max_before_x_factor,
    "max_before_x_mod": max_before_x_factor_mod,
    "min_before_x": min_before_x_factor,
    "min_before_x_mod":  min_before_x_factor_mod,
    "max_after_x": max_after_x_factor,
    "max_after_x_mod": max_after_x_factor_mod,
    "min_after_x": min_after_x_factor,
    "min_after_x_mod": min_after_x_factor_mod,
    "max_before_y": max_before_constant,
    "max_before_y_mod": max_before_constant_mod,
    "min_before_y": min_before_constant,
    "min_before_y_mod":  min_before_constant_mod,
    "max_after_y": max_after_constant,
    "max_after_y_mod": max_after_consatnt_mod,
    "min_after_y": min_after_constant,
    "min_after_y_mod": min_after_constant_mod,      
}
output_dict["modfits"] = mod_fits_dict

with open(args.output_path, "w") as out_f:
    json.dump(output_dict, out_f, indent=4)
