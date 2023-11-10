import argparse
import csv
import re

parser = argparse.ArgumentParser(prog="plot_dists.py", description="Plots the differences of specified satellite modules from specified CSV.")

parser.add_argument("csv_path", help="Path of csv file with (distance SGP4/Kepler at sim. second) vectors per satellite module.")
parser.add_argument('sat_mods', metavar='leo_modname', type=str, nargs='+', help='a satellite module name, leo...[...]')

args = parser.parse_args()
csv_path = args.csv_path
sat_mods = args.sat_mods
modname_re = r"leo.*]"

with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter="\t")
    header = "\t".join(row_reader.__next__()) + "\n"

    is_reading_mod_coords = False
    mod_rows = []
    current_mod = ""
    for row in row_reader:
        leo_modname = re.search(modname_re, "".join(row)).group()
        if leo_modname in sat_mods:
            print(leo_modname)
            # still reading
            if is_reading_mod_coords:
                mod_rows.append("\t".join(row) + "\n")
            # new coord list for mod found
            else:
                mod_rows = ["\t".join(row) + "\n"]
                is_reading_mod_coords = True
            
            current_mod = leo_modname

        else:
            # reading done
            if is_reading_mod_coords:
                modcsv_path = ("/".join( csv_path.split("/")[:-1] ) + 
                                "/satmod_csv/" + 
                                csv_path.split("/")[-1].removesuffix(".csv") + 
                                "_" + current_mod + ".csv")
                print(mod_rows)
                print(modcsv_path)
                lines = [header] + mod_rows
                with open (modcsv_path, "w") as satmod_csv_f:
                    satmod_csv_f.writelines(lines)
                
                is_reading_mod_coords = False
            # was not reading / nothing to read yet
            else:
                pass