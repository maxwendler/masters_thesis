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

import os
import sys
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.satname_to_modname import satname_to_modname
import argparse

parser = argparse.ArgumentParser(prog="get_modnames.py",
                                 description="""Creates file of OMNeT++ module names of a TLE set, so that output files 
                                                for the corresponding results from OMNeT++ simulation can be requested. 
                                                Satellite name to module name transformation matches module 
                                                name creation in SatelliteInserter class.""")
parser.add_argument("tles_path", help=".txt containing TLEs")
parser.add_argument("output_path")
args = parser.parse_args()

modnames = []
with open(args.tles_path, "r") as tles_f:
    lines = tles_f.readlines()
    for i in range(0, len(lines), 3):
        satname = lines[i].removesuffix("\n")
        modnames.append(satname_to_modname(satname))

with open(args.output_path, "w") as out_f:
    out_f.write("\n".join(modnames))