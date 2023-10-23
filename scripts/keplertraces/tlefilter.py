from sgp4.api import Satrec
from astropy.time import Time
from astropy import units as u
from poliastro.util import time_range
from datetime import datetime
from math import pi
from typing import Tuple
import os
from tleparse import get_avg_epoch_str

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
    tles_dir_path = '/workspaces/ma-max-wendler/scripts/keplertraces/tles/examples (requested at 2023-10-23-11-06-08)/'
    
    print("filtering TLE lists from ", tles_dir_path, "...\n")
    
    tles_fnames = os.listdir(tles_dir_path)
    
    # find cubesat and satnogs tle list to get walltime from filename
    try:
        satnogs_fname = [match for match in tles_fnames if match.startswith("satnogs_")][0]
    except: 
        IndexError("No SATNOGs constellation file starting with 'satnogs_' found.")
    
    try:
        cubesat_fname = [match for match in tles_fnames if match.startswith("cubesat_")][0]
    except:
        IndexError("No Cubesat constellation file starting with 'cubesat_' found.")

    satnogs_tles_path = tles_dir_path + satnogs_fname
    cubesat_tles_path = tles_dir_path + cubesat_fname
    
    # get satnogs leo list, satnogs leo eccentric list
    with open(satnogs_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    satnogs_leo_lines, satnogs_eccentric_lines = filter_tles_leo_ecc(org_lines)
    
    # get cubesat eccentric lines, cubesat_leo_lines won't be used
    with open(cubesat_tles_path, "r") as tles_f:
        org_lines = tles_f.readlines()
    cubesat_leo_lines, cubesat_eccentric_lines = filter_tles_leo_ecc(org_lines)

    # flag old satnogs and cubesat tles list as invalid by adding "_" as name prefix
    os.rename(satnogs_tles_path, satnogs_tles_path.removesuffix(satnogs_fname) + "_" + satnogs_fname)
    os.rename(cubesat_tles_path, cubesat_tles_path.removesuffix(cubesat_fname) + "_" + cubesat_fname)

    # get wall time of average TLE epoch string for remaining satnogs satellites
    satnogs_avg_walltime = get_avg_epoch_str(satnogs_leo_lines)
    # write satnogs leo file
    with open(tles_dir_path + "satnogs_leo_" + satnogs_avg_walltime, "w") as tles_f:
        tles_f.writelines(satnogs_leo_lines)
    
    print("filtered",
          int( (len(satnogs_eccentric_lines) + len(cubesat_eccentric_lines) / 3) ),
          "eccentric LEO satellites overall")

    satnogs_ecc_avg_walltime = get_avg_epoch_str(satnogs_eccentric_lines)
    # write satnogs eccentric file    
    with open(tles_dir_path + "satnogsEccentric_" + satnogs_ecc_avg_walltime, "w") as tles_f:
        tles_f.writelines(satnogs_eccentric_lines)
    
    cubesat_ecc_avg_walltime = get_avg_epoch_str(cubesat_eccentric_lines)
    # write cubesat eccentric file
    with open(tles_dir_path + "cubesatEccentric.txt_" + cubesat_ecc_avg_walltime, "w") as tles_f:
        tles_f.writelines(cubesat_eccentric_lines)