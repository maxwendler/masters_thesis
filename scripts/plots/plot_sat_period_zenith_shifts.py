import argparse
import json
import plotly.graph_objects as go

parser = argparse.ArgumentParser(prog="plot_sat_period_shifts.py", 
                                 description="""Plots zenith shifts of overlapping communication periods of two mobilities for the same satellite module
                                 as a function of time distance to the used TLE's epoch.""")
parser.add_argument("comm_comp_json", help="Path of the communication comparison JSON of the satellite module and the two mobilities.")
parser.add_argument("output_path")
args = parser.parse_args()

# get data
mobilties = args.comm_comp_json.split("/")[-1].split("_")[0].split("-")
ref_mobility = mobilties[0]
new_mobility = mobilties[1]

with open(args.comm_comp_json, "r") as json_f:
    comm_comp = json.load(json_f)

zenith_shifts = []
offsets_to_epoch = []

for p_group in comm_comp["period_groups"]:
    zenith_shifts.append(p_group["zenith_shift"])
    offsets_to_epoch.append(p_group["ref_start_to_epoch_offset"])

# plot data
fig = go.Figure(data=go.Scatter(x=offsets_to_epoch, y=zenith_shifts, mode='lines+markers'))

fig.update_layout(title_text=f'{ref_mobility}-{new_mobility} zenith shifts relative to TLE epoch at second 0')
fig.update_xaxes(title_text='seconds to epoch')
fig.update_yaxes(title_text='zenith shift in seconds')

# epoch line marker and annotation
if len(zenith_shifts) > 0:
    fig.add_shape(
        type="line",
        x0=0, y0=min(0, min(zenith_shifts)), x1=0, y1=max(zenith_shifts),
        line=dict(color="Red", width=1, dash="dash")
    )

    fig.add_annotation(
        x=0, y=max(zenith_shifts),
        text="epoch of satellite",
        showarrow=False,
        font=dict(size=14, color="Red")
    )

fig.write_image(args.output_path)