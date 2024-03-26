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

import re

name_hyphen_num_re = r"(\w+-\d+(?:\s.*)*)"
name_whitespace_num_re = r"(\w+\s\d+(?:\s.*)*)"
no_num_re = r"(\w+([\s,-].*\D+.*)*)"

def satname_to_modname(satname: str) -> str:
    """
    Converts a satellite name as it occurs in TLEs to its adapted form in the OMNET++ simulation.
    """

    # adaptation in create_traces.py, or SatelliteInserter.cc when no traces are used
    satname = satname.replace("/","-")
    
    # adaptations in SatelliteInserter.cc
    satname = satname.replace(".","-")
    modname = ""

    if re.fullmatch(name_hyphen_num_re, satname):
        constellation_and_remainder = satname.split("-", maxsplit=1)
        modname = constellation_and_remainder[0]
        satnum_and_remainder = constellation_and_remainder[1].split(" ", 1)
        if len(satnum_and_remainder) > 1:
            modname += satnum_and_remainder[1]
        modname += f"[{str(int(satnum_and_remainder[0]))}]"
    
    elif re.fullmatch(name_whitespace_num_re, satname):
        constellation_and_remainder = satname.split(" ", 1)
        modname = constellation_and_remainder[0]
        satnum_and_remainder = constellation_and_remainder[1].split(" ", 1)
        if len(satnum_and_remainder) > 1:
            modname += satnum_and_remainder[1]
        modname += f"[{str(int(satnum_and_remainder[0]))}]"
    
    elif re.fullmatch(no_num_re, satname):
        modname = satname + "[1]"
    
    else:
        raise NameError(f"Format of satellite {satname} is not supported!")
    
    modname = modname.replace(" ","")
    modname = "leo" + modname

    return modname