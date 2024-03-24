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

parser = argparse.ArgumentParser(prog="update_nod_xml.py", description="Inserts given string of node elements in given *.nod.xml.template.")
parser.add_argument("nod_xml_path")
parser.add_argument("nodes_str")
parser.add_argument("output_path")
args = parser.parse_args()

nodes_str = args.nodes_str.replace("\\n", "\n")

out_lines = []
# read template
with open(args.nod_xml_path) as in_xml:
    org_lines = in_xml.readlines()

# find line after <nodes> opening tag and insert node elements there
insert_in_next_line = False
for line_idx in range(len(org_lines)):
    line = org_lines[line_idx]
    if insert_in_next_line:
        out_lines.append(nodes_str)
        insert_in_next_line = False
    else:
        line = line.removesuffix("\n")
        out_lines.append(line)
    if "<nodes>" in line:
        insert_in_next_line = True

with open(args.output_path, "w") as out_xml:
    out_xml.write("\n".join(out_lines))