from sgp4.api import Satrec
from astropy.time import Time
from astropy import units as u
from poliastro.util import time_range
from datetime import datetime
from math import pi
from typing import Tuple

def filter_tles_leo_ecc(tle_lines: list[str]) -> Tuple[list[str], list[str]]:

    leo_lines = []
    eccentric_lines = []
    sat_num = 0
    filtered_leo_sat_num = 0
    filtered_ecc_sat_num = 0

    for i in range(0, len(tle_lines), 3):
        sat_name = tle_lines[i]
        tle_first = tle_lines[i + 1]
        tle_second = tle_lines[i + 2]

        satellite = Satrec.twoline2rv(tle_first, tle_second)
        sat_num += 1
        # in mean earth radii (6371008.7714m)
        max_alt_km = satellite.alta * 6371.0087714
        if not max_alt_km > 2000:
            if satellite.ecco > 0.04:
                eccentric_lines.append(sat_name)
                eccentric_lines.append(tle_first)
                eccentric_lines.append(tle_second)
                print("filtered eccentric LEO satellite", sat_name.removesuffix("\n"))
                filtered_ecc_sat_num += 1
            else:
                leo_lines.append(sat_name)
                leo_lines.append(tle_first)
                leo_lines.append(tle_second)
        else:
            print("filtered non-LEO satellite", sat_name.removesuffix("\n"))
            filtered_leo_sat_num += 1

    print("\n")
    print("filtered", filtered_leo_sat_num , "non-LEO satellites from", sat_num)
    print("filtered", filtered_ecc_sat_num, "eccentric LEO satellites from ", sat_num, "\n")
    return leo_lines, eccentric_lines
            
if __name__ == "__main__":
    
    org_lines = []
    tles_dir_path = "/workspaces/ma-max-wendler/scripts/keplertraces/tles/examples/"
    satnogs_tles_path = tles_dir_path + "satnogs_2023-10-19-13-20-16.txt"
    cubesat_tles_path = tles_dir_path + "cubesat_2023-10-19-13-20-20.txt"
    print("filtering", satnogs_tles_path, "...\n")
    
    with open(satnogs_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    satnogs_leo_lines, eccentric_lines = filter_tles_leo_ecc(org_lines)
    
    with open(cubesat_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    cubesat_leo_lines, cubesat_eccentric_lines = filter_tles_leo_ecc(org_lines)
    eccentric_lines += cubesat_eccentric_lines

    with open(satnogs_tles_path.removesuffix(".txt") + "_leo.txt", "w") as tles_f:
        tles_f.writelines(satnogs_leo_lines)

    print("filtered", int(len(eccentric_lines) / 3), "eccentric LEO satellites overall")
    with open(tles_dir_path + "eccentric_tles_satnogs_cubesat.txt", "w") as tles_f:
        tles_f.writelines(eccentric_lines)