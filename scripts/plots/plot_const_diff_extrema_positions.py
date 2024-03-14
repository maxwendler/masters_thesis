import csv
from datetime import datetime
from numpy import datetime64
from astropy.time import Time, TimeDelta
from math import floor
import os, sys
sys.path.append(os.path.join(sys.path[0],"..", ".."))
from scripts.keplertraces.tleparse import read
from scripts.utility.satname_to_modname import satname_to_modname
import argparse
import plotly.graph_objects as go


parser = argparse.ArgumentParser()
parser.add_argument("constellation")
parser.add_argument("tles_path")
parser.add_argument("diff_csv_path")
parser.add_argument("mob1_pos_csv_path")
parser.add_argument("mob1")
parser.add_argument("mob2_pos_csv_path")
parser.add_argument("mob2")
parser.add_argument("output_basepath")
parser.add_argument("--only_mod")
args = parser.parse_args()

start_datetime = datetime.strptime(args.tles_path.split("_")[-1].removesuffix(".txt"), '%Y-%m-%d-%H-%M-%S')
start = Time(datetime64(start_datetime), format="datetime64")
end = start + TimeDelta(43205, format="sec")

tles = read(args.tles_path)
sat_counter = 0
categories = []
values = []
output_lines = []
for tle in tles:
    
    satname = tle.name
    modname = satname_to_modname(satname)
    
    if args.only_mod:
        if modname != args.only_mod:
            continue

    meanmotion = tle.n
    orbital_period = 86400 / meanmotion
    
    mod_epoch = tle.epoch
    mod_epoch.format = "datetime64"
    start_to_epoch_sec = mod_epoch - TimeDelta(2000, format="sec") - start
    start_to_epoch_sec.format = "sec"
    epoch_to_end_sec = end - (mod_epoch + TimeDelta(2000, format="sec"))
    epoch_to_end_sec.format = "sec"

    mod_diffs = None
    with open(args.diff_csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f)
        header = row_reader.__next__()
        for row in row_reader:
            if row[0] == modname:
                mod_diffs = [float(diff) for diff in row[1:]]
                break
    
    # periods from start
    # find inclining part

    prev = None
    incline_idx = 0
    for i in range(len(mod_diffs)):
        
        diff = mod_diffs[i] 
        
        if not prev:
            prev = diff
        
        else:
            if diff > prev:
                incline_idx = i
                break
            prev = diff
    
    periods_start_to_epoch = floor((start_to_epoch_sec.value - incline_idx) / orbital_period)
    max_times = []
    min_times = []
    for i in range(periods_start_to_epoch):
        start_sec = incline_idx + int(i * orbital_period)
        end_sec = incline_idx + int((i + 1) * orbital_period)
        period_diffs = mod_diffs[start_sec:end_sec]
        max_times.append(start_sec + period_diffs.index(max(period_diffs)))
        min_times.append(start_sec + period_diffs.index(min(period_diffs)))
    
    # periods from right analogously
    prev = None
    incline_idx = 0
    for i in reversed(list(range(len(mod_diffs)))):
        
        diff = mod_diffs[i] 
        
        if not prev:
            prev = diff
        
        else:
            if diff > prev:
                incline_idx = i
                break
            prev = diff
    
    periods_end_to_epoch = floor(( epoch_to_end_sec.value - (43205 - incline_idx)) / orbital_period)
    max_times_to_append = []
    min_times_to_append = []
    for i in range(periods_end_to_epoch):
        end_sec = incline_idx - int(i * orbital_period) + 1
        start_sec = incline_idx - int((i + 1) * orbital_period) + 1
        
        period_diffs = mod_diffs[start_sec:end_sec]
        max_times_to_append.append(start_sec + period_diffs.index(max(period_diffs)))
        min_times_to_append.append(start_sec + period_diffs.index(min(period_diffs)))
    max_times += reversed(max_times_to_append)
    min_times += reversed(min_times_to_append)

    mod_pos_mob1 = []
    with open(args.mob1_pos_csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f, delimiter="\t")
        header = row_reader.__next__()
        was_reading = False 
        for row in row_reader:
            if modname in row[2]:
                was_reading = True
                mod_pos_mob1.append(tuple([float(coord) for coord in row[3:]]))
            if modname not in row[2] and was_reading:
                break

    mod_pos_mob2 = []
    with open(args.mob2_pos_csv_path, "r") as csv_f:
        row_reader = csv.reader(csv_f, delimiter="\t")
        header = row_reader.__next__()
        was_reading = False 
        for row in row_reader:
            if modname in row[2]:
                was_reading = True
                mod_pos_mob2.append(tuple([float(coord) for coord in row[3:]]))
            if modname not in row[2] and was_reading:
                break
    
    max_times_zs_mob1 = []
    min_times_zs_mob1 = []
    max_times_zs_mob2 = []
    min_times_zs_mob2 = []
    output_lines.append(f"+++{satname}+++")
    output_lines.append("---max---")
    output_lines.append(str(max_times))
    for t in max_times:
        max_times_zs_mob1.append(mod_pos_mob1[t][2])
        output_lines.append(f"{args.mob1} {mod_pos_mob1[t]}")
        max_times_zs_mob2.append(mod_pos_mob2[t][2])
        output_lines.append(f"{args.mob2} {mod_pos_mob2[t]}")
    output_lines.append("---min---")
    output_lines.append(str(min_times))
    for t in min_times:
        min_times_zs_mob1.append(mod_pos_mob1[t][2])
        output_lines.append(f"{args.mob1} {mod_pos_mob1[t]}")
        min_times_zs_mob2.append(mod_pos_mob2[t][2])
        output_lines.append(f"{args.mob2} {mod_pos_mob2[t]}")
    
    values += max_times_zs_mob1 + max_times_zs_mob2 + min_times_zs_mob1 + min_times_zs_mob2
    categories += [f"max {args.mob1}"] * len(max_times_zs_mob1) + [f"max {args.mob2}"] * len(max_times_zs_mob2) + [f"min {args.mob1}"] * len(min_times_zs_mob1) + [f"min {args.mob2}"] * len(min_times_zs_mob2)
    sat_counter += 1
    print(f"{args.constellation} {sat_counter}/{len(tles)} satellites")

fig = go.Figure(data=go.Scatter(x=categories, y=values, mode='markers'))
fig.update_yaxes(title_text="ITRF z coord. in km")

fig.write_image(args.output_basepath + "max_min_zs.svg")
with open(args.output_basepath + "max_min_coords.txt", "w") as out_txt:
    out_txt.write("\n".join(output_lines))    