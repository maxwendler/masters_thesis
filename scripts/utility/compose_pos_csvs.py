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

parser = argparse.ArgumentParser(prog="compose_pos_csvs.py", 
                                 description="Merges multiple CSV files under header of first provided file by appending lines of the following files.")
parser.add_argument("output_path")
parser.add_argument("in_csvs", nargs="+")
args = parser.parse_args()

# lines for output file buffer
out_csv_lines = []
# used as flag for header existence
header = None

# read header from first file + all lines except header to buffer
for path in args.in_csvs:
    
    with open(path, "r") as in_csv:
        rows = in_csv.readlines()
        if not header:
            header = rows[0]
            out_csv_lines.append(header)
    
        out_csv_lines += rows[1:]

with open(args.output_path, "w") as out_csv:
    out_csv.writelines(out_csv_lines)