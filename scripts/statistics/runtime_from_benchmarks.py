import argparse

parser = argparse.ArgumentParser()
parser.add_argument("output_path")
parser.add_argument("benchmark_paths", nargs="+")
args = parser.parse_args()

runtime_sec = 0
for path in args.benchmark_paths:
    with open(path, "r") as benchmark_f:
        vals_line = benchmark_f.readlines()[1]
        sec_val = float(vals_line.split("\t")[0])
        runtime_sec += sec_val

with open(args.output_path, "w") as out_f:
    out_f.write("\n".join(["s", str(runtime_sec)]))