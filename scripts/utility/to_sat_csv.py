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

satmod_lines = []
with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter="\t")
    header = "\t".join(row_reader.__next__())

    is_reading_mod_coords = False
    mod_rows = []
    current_mod = ""
    for row in row_reader:
        leo_modname = re.search(modname_re, "".join(row)).group()
        if leo_modname in sat_mods:

            # still reading
            if is_reading_mod_coords:
                mod_rows.append("\t".join(row))
            # new coord list for mod found
            else:
                mod_rows = ["\t".join(row)]
                is_reading_mod_coords = True
            
            current_mod = leo_modname

        else:
            # reading done
            if is_reading_mod_coords:
                
                satmod_lines = [header] + mod_rows

                # output to file instead of print for testing purposes
                """
                modcsv_path = ("/".join( csv_path.split("/")[:-1] ) + 
                                "/satmod_csv/" + 
                                csv_path.split("/")[-1].removesuffix(".csv") + 
                                "_" + current_mod + ".csv")
                
                # with open (modcsv_path, "w") as satmod_csv_f:
                #    satmod_csv_f.writelines(satmod_lines)
                """
                is_reading_mod_coords = False
                sat_mods.remove(current_mod)
                if len(sat_mods) == 0:
                    break
            
            # was not reading / nothing to read yet
            else:
                pass
            
# satmod_lines need to be created here when csv only contains rows for one specified module
# or it is in the last rows
if len(mod_rows) > 0 and len(satmod_lines) == 0:
    satmod_lines = [header] + mod_rows
    
print("\n".join(satmod_lines))