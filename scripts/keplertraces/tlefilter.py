from sgp4.api import Satrec
from astropy.time import Time
from astropy import units as u
from poliastro.util import time_range
from datetime import datetime
from math import pi
from typing import Tuple

def filter_tles_leo_ecc(tle_lines: list[str]) -> Tuple[list[str], list[str]]:
    """
    Parses a list of str-based TLEs to sgp4 Satrec instances and filters them,
    returning 
    (1) a list of TLEs for satellites with apoapsis <= 2000 km and eccentricity <= 0.04 
    (2) a list of TLEs for satellites with apoapsis <= 2000 km and eccentricity > 0.04
    (must contain only TLEs, each TLE must be three lines [name, line1, line2])
    """

    leo_lines = []
    eccentric_lines = []
    sat_num = 0
    filtered_leo_sat_num = 0
    filtered_ecc_sat_num = 0

    for i in range(0, len(tle_lines), 3):
        
        # current TLE lines
        sat_name = tle_lines[i]
        tle_first = tle_lines[i + 1]
        tle_second = tle_lines[i + 2]

        satellite = Satrec.twoline2rv(tle_first, tle_second)
        sat_num += 1
        
        # 'alta' in mean earth radii (mean radius = 6371008.7714m)
        # see Moritz, H. (1980). Geodetic reference system 1980. Bulletin géodésique, 54(3), 395-405
        apoapsis_altitude = satellite.alta * 6371.0087714
        
        if not apoapsis_altitude > 2000:

            if satellite.ecco > 0.04:
                # eccentric LEO satellites
                eccentric_lines.append(sat_name)
                eccentric_lines.append(tle_first)
                eccentric_lines.append(tle_second)
                print("filtered eccentric LEO satellite", sat_name.removesuffix("\n"))
                filtered_ecc_sat_num += 1
            
            else:
                # LEO satellites
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
    
    # get satnogs leo list, eccentric list
    with open(satnogs_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    satnogs_leo_lines, eccentric_lines = filter_tles_leo_ecc(org_lines)
    
    # append eccentric list, cubesat_leo_lines won't be used
    with open(cubesat_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    cubesat_leo_lines, cubesat_eccentric_lines = filter_tles_leo_ecc(org_lines)
    eccentric_lines += cubesat_eccentric_lines

    # write satnogs leo file
    with open(satnogs_tles_path.removesuffix(".txt") + "_leo.txt", "w") as tles_f:
        tles_f.writelines(satnogs_leo_lines)

    # write eccentric file
    print("filtered", int(len(eccentric_lines) / 3), "eccentric LEO satellites overall")
    with open(tles_dir_path + "eccentric_tles_satnogs_cubesat.txt", "w") as tles_f:
        tles_f.writelines(eccentric_lines)