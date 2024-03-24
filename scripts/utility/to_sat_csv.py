"""
Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import argparse
import csv
import re

parser = argparse.ArgumentParser(prog="to_sat_csv.py", description="Prints specified satellite module coordinates CSV lines from coordinates CSV of all constellation satellite modules.")

parser.add_argument("csv_path", help="Path of CSV with constellation coordinates.")
parser.add_argument('sat_mod', help='a satellite module name, leo...[...]')

args = parser.parse_args()
csv_path = args.csv_path
sat_mod = args.sat_mod
modname_re = r"leo.*]"

satmod_lines = []
with open(csv_path, "r") as csv_f:
    
    row_reader = csv.reader(csv_f, delimiter="\t")
    header = "\t".join(row_reader.__next__())

    is_reading_mod_coords = False
    mod_rows = []
    current_mod = ""

    # one 3D coord per line -> find lines of specified modules
    for row in row_reader:
        leo_modname = re.search(modname_re, "".join(row)).group()
        if leo_modname == sat_mod:

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
                break
            # was not reading / nothing to read yet
            else:
                pass
            
# satmod_lines need to be created here when csv only contains rows for one specified module
# or it is in the last rows
if len(mod_rows) > 0 and len(satmod_lines) == 0:
    satmod_lines = [header] + mod_rows
    
print("\n".join(satmod_lines))