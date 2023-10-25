import argparse

CONFIG_TEMPLATE_PATH = "/workspaces/ma-max-wendler/scripts/keplertraces/config_template.txt"

def update(ini_path: str, tles_paths: list[str], traces_dir_path: str):
    
    # load config template
    template_str = None    
    with open(CONFIG_TEMPLATE_PATH, "r") as template_f:
        template_str = template_f.read()
    
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
        new_lines.append(line)
    
    # add configurations for TLE lists
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
        kepler_config_lines.pop(6)
        new_lines += kepler_config_lines

        # sgp4 config, needs path of TLE list
        sgp4_config_str = str(config_str)
        sgp4_config_str = sgp4_config_str.replace("$CONSTELLATION$", constellations[i] + "-sgp4")
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_TYPE$", f'"SGP4"')
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_CLASS$", f'"SGP4Mobility"')
        sgp4_config_str = sgp4_config_str.replace("$TLE_PATH$", f'"{tles_paths[i]}"')
        sgp4_config_lines = sgp4_config_str.splitlines(keepends=True)
        sgp4_config_lines.pop(7)
        new_lines += sgp4_config_lines

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
    parser.add_argument('traces_dir', help="Path of directory containing directories of traces indiviual TLE lists (named after TLE list files by 'create_traces.py').")
    parser.add_argument('tles_paths', metavar='tle_path', type=str, nargs='+', help='Path of a TLE list.')

    args = parser.parse_args()
    update(args.ini_path, args.tles_paths , args.traces_dir)