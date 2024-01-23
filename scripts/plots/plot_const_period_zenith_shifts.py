import argparse
import json
import os
import plotly.graph_objects as go
from numpy.polynomial import Polynomial

parser = argparse.ArgumentParser(prog="plot_const_period_zenith_shifts",
                                 description="""Plots zenith shifts of overlapping communication periods of two mobilities for all satellite modules
                                 of a constellation as a function of time distance to the used TLE's epoch.""")
parser.add_argument("comm_comp_dir", help="Directory with all the communication comparison JSONs of a constellation.")
parser.add_argument("svg_output_path")
parser.add_argument("--differences", action="store_true", help="If flag is set, plots absolute values of zenith shifts.")
args = parser.parse_args()

comm_comp_dir = args.comm_comp_dir if args.comm_comp_dir.endswith("/") else args.comm_comp_dir + "/"
ref_mobility = None 
new_mobility = None

# get data as (offset to epoch, zenith shift, modname) tuples
data = []
for comm_comp_fname in filter(lambda fname: fname.endswith("communication_comparison.json"), os.listdir(comm_comp_dir)):
    
    if not ref_mobility:
        mobilties = comm_comp_fname.split("_")[0].split("-")
        ref_mobility = mobilties[0]
        new_mobility = mobilties[1]

    comm_comp_path = comm_comp_dir + comm_comp_fname
    with open(comm_comp_path, "r") as json_f:
        comm_comp = json.load(json_f)
    
    for p_group in comm_comp["period_groups"]:
        if args.differences:
            data.append( tuple( [p_group["ref_start_to_epoch_offset"], abs(p_group["zenith_shift"]), comm_comp["modname"]] ) )
        else:
            data.append( tuple( [p_group["ref_start_to_epoch_offset"], p_group["zenith_shift"], comm_comp["modname"]] ) )

# sort by offset to epoch
data.sort(key=lambda data_tuple: data_tuple[0])

if len(data) == 0:
    fig = go.Figure()
    fig.add_annotation(dict(font=dict(color="black",size=40),
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    text="No common communication for which intervals exist.",
                    textangle=0,
                    xref="paper",
                    yref="paper"))

else:

    # create point plot with modname annotation for every point
    offsets = []
    pos_offsets = []
    zenith_shifts = []
    pos_offset_zenith_shifts = []

    for i in range(len(data)):
        
        offset = data[i][0]
        zenith_shift = data[i][1]
        
        offsets.append(offset)
        zenith_shifts.append(zenith_shift)

        if offset >= 0:
            pos_offsets.append(offset)
            pos_offset_zenith_shifts.append(zenith_shift)
        

    fig = go.Figure(data=go.Scatter(x=offsets, y=zenith_shifts, mode='markers'))
    fig.update_xaxes(title_text='seconds to epoch')
    fig.update_yaxes(title_text='zenith shift in seconds')
    fig.update_layout(title_text=f'{ref_mobility}-{new_mobility} zenith shifts relative to TLE epoch at second 0')

    if len(pos_offsets) > 1:
    
        linear_fun = Polynomial.fit(pos_offsets, pos_offset_zenith_shifts, deg=1)
        linear_fun_xs = [0, max(pos_offsets)]
        linear_fun_ys = [linear_fun(0), linear_fun(linear_fun_xs[1])]
        fig.add_trace(go.Scatter(x=linear_fun_xs, y=linear_fun_ys, mode='lines', line=dict(color="blue", dash="dash")))
        fig.update_layout(title_text=f'{ref_mobility}-{new_mobility} zenith shifts relative to TLE epoch at second 0: {str(linear_fun.convert())}')

    # estimate from just trying!
    average_pixel_width_per_char = 6
    padding = 0
    yshift_sign = 1

    # modname annotations
    for data_tuple in data:

        modname = data_tuple[2]
        yshift = (len(modname) * average_pixel_width_per_char / 2 + padding) * yshift_sign
        yshift_sign *= -1

        fig.add_annotation(
            x=data_tuple[0], y=data_tuple[1],
            text=data_tuple[2],
            showarrow=False,
            font=dict(size=4, color="Black"),
            textangle=90,
            yshift=yshift
        )

fig.write_image(args.svg_output_path, width=1920, height=1080)
fig.write_html(args.svg_output_path.removesuffix("svg") + "html")