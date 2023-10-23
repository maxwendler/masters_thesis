import os

CONFIG_TEMPLATE_PATH = "./config_template.txt"

def update(ini_path: str, tles_dir_path: str, tles_fnames: list[str], traces_dir_path: str):
    
    template_str = None    
    with open(CONFIG_TEMPLATE_PATH, "r") as template_f:
        template_str = template_f.read()
    
    constellations = []
    wall_clock_start_times = []
    for fname in tles_fnames:
        tles_params = fname.removesuffix(".txt").split("_")
        constellations.append(tles_params[0])
        wall_clock_start_times.append(tles_params[-1])

    org_ini_lines = None
    with open(ini_path, "r") as ini_f:
        org_ini_lines = ini_f.readlines()
    
    debug_section_found = False
    new_lines = []
    for i in range(0, len(org_ini_lines)):
        line = org_ini_lines[i]
        if "[Config" in line and debug_section_found:
            break
        if "[Config Debug]" in line:
            debug_section_found = True
        new_lines.append(line)
    
    for i in range(0, len(tles_fnames)):
        config_str = str(template_str)
        config_str = config_str.replace("$WALL_START_TIME$", f'"{wall_clock_start_times[i]}"')

        kepler_config_str = str(config_str)
        kepler_config_str = kepler_config_str.replace("$CONSTELLATION$", constellations[i] + "-kepler")
        kepler_config_str = kepler_config_str.replace("$MOBILITY_TYPE$", f'"Kepler"')
        kepler_config_str = kepler_config_str.replace("$MOBILITY_CLASS$", f'"KeplerMobility"')
        kepler_config_str = kepler_config_str.replace("$TRACES_PATH$", f'"{traces_dir_path}{tles_fnames[i].removesuffix(".txt")}/"')
        kepler_config_lines = kepler_config_str.splitlines(keepends=True)
        kepler_config_lines.pop(6)
        new_lines += kepler_config_lines

        print(tles_fnames)

        sgp4_config_str = str(config_str)
        sgp4_config_str = sgp4_config_str.replace("$CONSTELLATION$", constellations[i] + "-sgp4")
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_TYPE$", f'"SGP4"')
        sgp4_config_str = sgp4_config_str.replace("$MOBILITY_CLASS$", f'"SGP4Mobility"')
        sgp4_config_str = sgp4_config_str.replace("$TLE_PATH$", f'"{tles_dir_path}{tles_fnames[i]}"')
        sgp4_config_lines = sgp4_config_str.splitlines(keepends=True)
        sgp4_config_lines.pop(7)
        new_lines += sgp4_config_lines

    os.rename(ini_path, ini_path.removesuffix("omnetpp.ini") + "_" + "omnetpp.ini")

    with open(ini_path, "w") as new_ini_f:
        new_ini_f.writelines(new_lines)

if __name__ == "__main__":
    tles_fname_prefixes = ["iridium-NEXT", "oneweb", "satnogs", "starlink", "cubesatEccentric", "satnogsEccentric"]
    tles_fnames = []
    tles_dir = "/workspaces/ma-max-wendler/scripts/keplertraces/tles/examples (requested at 2023-10-23-11-06-08)/"
    
    for fname in os.listdir(tles_dir):
        if fname.split("_")[0] in tles_fname_prefixes:
            tles_fnames.append(fname)
    
    traces_dir = "/workspaces/ma-max-wendler/examples/space_veins/traces/"

    update("/workspaces/ma-max-wendler/examples/space_veins/omnetpp.ini", tles_dir, tles_fnames, traces_dir)