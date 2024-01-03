import argparse
import csv
from operator import itemgetter

parser = argparse.ArgumentParser(prog="time_sort_csv.py", description="Sorts csv after columns node (1st) and time (2nd).")

parser.add_argument("csv_path", help="Path of the csv of simulation results.")

args = parser.parse_args()

rows = []
print(f"reading {args.csv_path} ...")
with open(args.csv_path) as csv_f:
    dict_reader = csv.DictReader(csv_f, delimiter="\t")
    
    for row in dict_reader:
        rows.append( tuple( [row["node"], [int(row["time"])], row] ) )

# sort by (1) node str and (2) time
rows.sort(key=itemgetter(0, 1))
# get actual rows from sorted tuples and add header
rows = [r[2] for r in rows]
header = "\t".join(rows[0].keys()) + "\n"
rows = [ ("\t".join(r.values()) + "\n") for r in rows]
rows = [header] + rows

# create output path
sorted_path = args.csv_path.removesuffix(".csv") + "_sorted.csv"
print(sorted_path)

with open(sorted_path, "w") as new_csv_f:
    new_csv_f.writelines(rows)

print(f"done ({sorted_path})")