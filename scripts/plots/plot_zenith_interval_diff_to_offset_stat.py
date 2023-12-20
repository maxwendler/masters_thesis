import argparse
import json
import plotly.graph_objects as go
from numpy.polynomial import Polynomial


parser = argparse.ArgumentParser(prog="plot_zenith_interval_diff_at_offset_sum")
parser.add_argument("zenith_interval_changes_json")
parser.add_argument("offset_stat", choices=["offset_sum", "offset_diff"])
parser.add_argument("output_path")
args = parser.parse_args()

with open(args.zenith_interval_changes_json, "r") as json_f:
    zenith_interval_changes = json.load(json_f)

interval_differences = [abs(interval_dict["difference"]) for interval_dict in zenith_interval_changes["same_periods_changes"].values()]

fig = None
if args.offset_stat == "offset_sum":
    offset_sums = [interval_dict["abs_offset_sum"] for interval_dict in zenith_interval_changes["same_periods_changes"].values()]
    fig = go.Figure(data=go.Scatter(x=offset_sums, y=interval_differences, mode='markers'))
    fig.update_xaxes(title_text='seconds sum to epoch')
else:
    offset_diffs = [interval_dict["abs_offset_diff"] for interval_dict in zenith_interval_changes["same_periods_changes"].values()]
    # fitting of linear function
    # fit linear function including outliers
    all_vals_fun = Polynomial.fit(offset_diffs, interval_differences, deg=1)
    # remove fixed num of outliers
    predictions = [all_vals_fun(x) for x in offset_diffs]
    errors = []
    for i in range(len(interval_differences)):
        diff = interval_differences[i]
        prediction = predictions[i]
        errors.append(abs(diff - prediction))
    
    inliers_fun_xs = [0, max(offset_diffs)]

    # find 4 most outlying points
    outlier_xs = []
    outlier_ys = []
    for i in range(4):
        outlier_idx = errors.index(max(errors))
        errors.pop(outlier_idx)
        outlier_xs.append(offset_diffs.pop(outlier_idx))
        outlier_ys.append(interval_differences.pop(outlier_idx))
    
    print("outliers:")
    print(outlier_xs)
    print(outlier_ys)

    # fit new linear function ignoring the outliers
    inliers_fun = Polynomial.fit(offset_diffs, interval_differences, deg=1)
    inliers_fun_ys = [inliers_fun(0), inliers_fun(inliers_fun_xs[1])]

    fig = go.Figure(data=go.Scatter(x=offset_diffs, y=interval_differences, mode='markers',line=dict(color="blue")))
    fig.update_xaxes(title_text='absolute seconds difference in offset to epoch')
    fig.update_layout(title=f"y={str(inliers_fun.convert())}")
    fig.add_trace(go.Scatter(x=outlier_xs, y=outlier_ys, mode='markers', line=dict(color="red")))
    fig.add_trace(go.Scatter(x=inliers_fun_xs, y=inliers_fun_ys, mode='lines', line=dict(color="blue", dash="dash")))

fig.update_yaxes(title_text='absolute interval difference in seconds')
fig.write_image(args.output_path)