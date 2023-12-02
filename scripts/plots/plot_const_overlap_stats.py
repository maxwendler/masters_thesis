import argparse
import json
import os
import plotly.express as px

parser = argparse.ArgumentParser(prog="plot_const_overlap_stats.py")
parser.add_argument("comp_info_dir")
parser.add_argument("output_path")
args = parser.parse_args()

modnames = []
avg_ref_coverages = []
excluded_times_to_ref_times = []

comp_info_dir = args.comp_info_dir if args.comp_info_dir.endswith("/") else args.comp_info_dir + "/"
info_json_paths = sorted( [ comp_info_dir + fname for fname in list( filter( lambda fname: fname.endswith("_communication_comparison.json"), os.listdir(comp_info_dir) ) ) ] ) 

for path in info_json_paths:

    with open(path, "r") as json_f:
        comm_periods = json.load(json_f)
        modnames.append(comm_periods["modname"])
        avg_ref_coverages.append( comm_periods["avg_ref_coverage"] )
        excluded_times_to_ref_times.append( comm_periods["total_excluded_time_to_ref_time"] )


modnames_for_df = []
for modname in modnames:
    modnames_for_df += [modname] * 2

vals_for_df = []
categories_for_df = []
for i in range(0, len(avg_ref_coverages)):
    vals_for_df.append(avg_ref_coverages[i])
    vals_for_df.append(excluded_times_to_ref_times[i])
    categories_for_df.append("avg_ref_coverage")
    categories_for_df.append("excluded_time_to_ref_time")

fig = px.histogram(x=modnames_for_df, y=vals_for_df, color=categories_for_df, barmode='group', labels={"y": "%"}, histfunc=None)
fig.write_image(args.output_path)
fig.write_html(args.output_path.removesuffix("png") + "html")