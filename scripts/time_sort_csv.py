import argparse
import csv
from operator import itemgetter

parser = argparse.ArgumentParser(prog="plot_dists.py", description="Sorts csv after columns node (1st) and time (2nd).")

parser.add_argument("csv_path", help="Path of the csv of simulation results.")

args = parser.parse_args()

rows = []
with open(args.csv_path) as csv_f:
    dict_reader = csv.DictReader(csv_f, delimiter="\t")
    
    for row in dict_reader:
        rows.append( tuple( [row["node"], [int(row["time"])], row] ) )

print(len(rows))
# sort by node str and time in
rows.sort(key=itemgetter(0, 1))
print(len(rows))
# get actual rows from sorted tuples and add header
rows = [r[2] for r in rows]
print(len(rows))
header = "\t".join(rows[0].keys()) + "\n"
rows = [ ("\t".join(r.values()) + "\n") for r in rows]
rows = [header] + rows
print(len(rows))
# turn dicts from DictReader to str

print(rows[:10])

with open(args.csv_path.removesuffix(".csv") + "_sorted.csv", "w") as new_csv_f:
    new_csv_f.writelines(rows)
