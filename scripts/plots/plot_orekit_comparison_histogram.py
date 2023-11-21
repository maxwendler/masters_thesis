import argparse
from plot_difference_distributions import parse_difference_csv
import plotly.express as px

parser = argparse.ArgumentParser(prog="plot_orekit_comparison_histogram.py")
parser.add_argument("no_orekit_distances_path")
parser.add_argument("orekit_distances_path")
parser.add_argument("output_path")
args = parser.parse_args()

satnames, no_orekit_distances = parse_difference_csv(args.no_orekit_distances_path)
satnames, orekit_distances = parse_difference_csv(args.orekit_distances_path)

satnames_for_df = []
colors_for_df = []
for name in satnames:
    satnames_for_df += [name] * len(orekit_distances[0]) * 2
    colors_for_df += ["no orekit"] * len(orekit_distances[0]) + ["orekit"] * len(orekit_distances[0])
distances_for_df = []

for i in range(0, len(orekit_distances)):
    distances_for_df += no_orekit_distances[i] + orekit_distances[i]

no_orekit_distsum = sum(sum(no_orekit_sat_dists) for no_orekit_sat_dists in no_orekit_distances)
orekit_diststum = sum(sum(orekit_sat_dists) for orekit_sat_dists in orekit_distances)
distsum_change = orekit_diststum - no_orekit_distsum
avg_dist_change = distsum_change / ( len(orekit_distances[0]) * len(orekit_distances) )

fig = px.histogram(x=satnames_for_df, y=distances_for_df, color=colors_for_df, barmode='group', labels={"x": f"change of avg. diff. sum: {distsum_change} km\n avg. change per coord diff.: {avg_dist_change} km"})
fig.write_html(args.output_path)