import argparse
import plotly.graph_objects as go
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("avg_differences_dir")
parser.add_argument("constellation")
parser.add_argument("output_path")
args = parser.parse_args()

avg_differences_dir = args.avg_differences_dir if args.avg_differences_dir.endswith("/") else args.avg_differences_dir + "/"

halforbit_tenth_re = r'halfOrbitTenth=\d+_'

avg_differences = []
halforbit_tenths = []
for fname in filter( lambda fname: fname.startswith(args.constellation + "_teme_sgp4-circular") and fname.endswith("avg_difference.txt") , os.listdir(avg_differences_dir) ):
    txt_path = avg_differences_dir + fname
    print(txt_path)
    halforbit_tenth = re.search(halforbit_tenth_re, txt_path).group()
    halforbit_tenths.append(int(halforbit_tenth.split("=")[1].removesuffix("_")))
    with open(txt_path, "r") as txt_f:
        avg_diff_line = txt_f.readlines()[1]
        avg_differences.append(float(avg_diff_line.split(" ")[1]))

fig = go.Figure(data=go.Scatter(x=halforbit_tenths, y=avg_differences, mode='lines+markers'))

fig.write_image(args.output_path)