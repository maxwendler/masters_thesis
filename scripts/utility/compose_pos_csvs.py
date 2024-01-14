import argparse

parser = argparse.ArgumentParser()
parser.add_argument("output_path")
parser.add_argument("in_csvs", nargs="+")
args = parser.parse_args()

out_csv_lines = []
header = None

for path in args.in_csvs:
    
    with open(path, "r") as in_csv:
        rows = in_csv.readlines()
        if not header:
            header = rows[0]
    
        out_csv_lines += rows[1:]

with open(args.output_path, "w") as out_csv:
    out_csv.writelines(out_csv_lines)