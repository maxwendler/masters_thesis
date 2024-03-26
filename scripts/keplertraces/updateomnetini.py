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

# importable function for omnetpp.ini as described at bottom of this file for direct script execution
def update(ini_path: str, tles_paths: list[str], conf_template_path: str, avg_sgp4_radii_paths: list[str], traces_dir_path: str, sim_time_limit: int, location: str):
    
    # load config template
    template_str = None    
    with open(conf_template_path, "r") as template_f:
        template_str = template_f.read()
    
    after_license_txt_idx = template_str.find("[Config")
    template_str = template_str[after_license_txt_idx:]

    # get filenames of tles and parse constellation name and average wall time
    tles_fnames = [tle_path.split("/")[-1] for tle_path in tles_paths]
    constellations = []
    wall_clock_start_times = []
    for fname in tles_fnames:
        tles_params = fname.removesuffix(".txt").split("_")
        constellations.append(tles_params[0])
        wall_clock_start_times.append(tles_params[-1])

    org_ini_lines = None
    with open(ini_path, "r") as ini_f:
        org_ini_lines = ini_f.readlines()
    
    # copy original file until (including) [Config Debug] section
    debug_section_found = False
    new_lines = []
    for i in range(0, len(org_ini_lines)):
        line = org_ini_lines[i]
        if "[Config" in line and debug_section_found:
            break
        if "[Config Debug]" in line:
            debug_section_found = True
        if line.startswith("sim-time-limit") and not debug_section_found:
            line = "sim-time-limit = ${simTimeLimit=" + str(sim_time_limit) + "}s\n"
        if line.startswith("*.sop.location"):
            line = '*.sop.location = ${location="' + location +'"}\n'
        new_lines.append(line)
    
    # add configurations for TLE lists
    print(constellations)
    for i in range(0, len(tles_fnames)):

        # same walltime for configs of all mobility models
        config_str = str(template_str)
        config_str = config_str.replace("$WALL_START_TIME$", f'"{wall_clock_start_times[i]}"')

        # kepler config, needs path of directory containing traces for constellation
        kepler_config_str = str(config_str)
        kepler_config_str = kepler_config_str.replace("$CONSTELLATION$", constellations[i] + "-kepler")
        kepler_config_str = kepler_config_str.replace("$MOBILITY_TYPE$", f'"Kepler"')
        kepler_config_str = kepler_config_str.replace("$MOBILITY_CLASS$", f'"KeplerMobility"')
        kepler_config_str = kepler_config_str.replace("$TRACES_PATH$", f'"{traces_dir_path}{tles_fnames[i].removesuffix(".txt")}/"')
        kepler_config_lines = kepler_config_str.splitlines(keepends=True)
        # remove TLE path line
        kepler_config_lines.pop(6)
        new_lines += kepler_config_lines

        # sgp4 config, needs path of TLE list
        sgp4_config_str = str(config_str)
        sgp4_config_str = sgp4_config_str.replace("$CONSTELLATION$", constellations[i] + "-sgp4")
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_TYPE$", f'"SGP4"')
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_CLASS$", f'"SGP4Mobility"')
        sgp4_config_str = sgp4_config_str.replace("$TLE_PATH$", f'"{tles_paths[i]}"')
        sgp4_config_lines = sgp4_config_str.splitlines(keepends=True)
        # remove traces path line
        sgp4_config_lines.pop(7)
        new_lines += sgp4_config_lines

        # circular config, needs path of TLE list
        circular_config_str = str(config_str)
        circular_config_str = circular_config_str.replace("$CONSTELLATION$", constellations[i] + "-circular")
        circular_config_str = circular_config_str.replace("$MOBILITY_TYPE$", f'"Circular"')
        circular_config_str = circular_config_str.replace("$MOBILITY_CLASS$", f'"CircularMobility"')
        circular_config_str = circular_config_str.replace("$TLE_PATH$", f'"{tles_paths[i]}"')
        circular_config_lines = circular_config_str.splitlines(keepends=True)
        # remove traces path line
        circular_config_lines.pop(7)
        # insert line for parameter study about which second circle plane point to choose 
        circular_config_lines.insert(7, "*.leo*[*].mobility.circlePlane2ndPointHalfOrbitTenth = 25\n")
        if i < len(avg_sgp4_radii_paths):
            if avg_sgp4_radii_paths[i] != "None":
                circular_config_lines.insert(7, "*.satelliteInserter.useAvgSGP4Radii = true\n")
                circular_config_lines.insert(7, "*.satelliteInserter.avgSGP4RadiiPath = " + f'"{avg_sgp4_radii_paths[i]}"' + "\n")
            else:
                circular_config_lines.insert(7, "*.satelliteInserter.useAvgSGP4Radii = false\n")
            new_lines += circular_config_lines

    input_ini_fname = ini_path.split("/")[-1] 
    with open(ini_path.removesuffix(input_ini_fname) + "omnetpp.ini", "w") as new_ini_f:
        new_ini_f.writelines(new_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="updateomnetini.py", 
                                     description=("Creates configurations with consistent walltime (from filenames) in the given" 
                                                  "omnetpp.ini (or .ini template), trace directory paths and TLE list paths."
                                                  "One configuration per (mobility model x TLE list).")
                                    )
    parser.add_argument('ini_path', help="Path of omnetpp.ini (for file update) or .ini template (for omnetpp.ini file).")
    parser.add_argument("conf_template")
    parser.add_argument('traces_dir', help="Path of directory containing directories of traces indiviual TLE lists (named after TLE list files by 'create_traces.py').")
    parser.add_argument('--tles_paths', "-t", metavar='tle_path', type=str, nargs='+', help='Path of a TLE list.')
    parser.add_argument('--avg_sgp4_radii_paths', metavar="avg_sgp4_radii_path", type=str, nargs="+")
    parser.add_argument('sim_time_limit', type=int)
    parser.add_argument('location')

    args = parser.parse_args()
    print(args.tles_paths)
    print(args.avg_sgp4_radii_paths)
    update(args.ini_path, args.tles_paths, args.conf_template, args.avg_sgp4_radii_paths, args.traces_dir, args.sim_time_limit, args.location)