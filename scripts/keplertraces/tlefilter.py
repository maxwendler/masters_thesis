from sgp4.api import Satrec
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
            
def filter_doubles(tle_lines: list[str]) -> list[str]:
    new_lines = []
    sat_names = []
    for i in range(0, len(tle_lines), 3):
        if tle_lines[i] not in sat_names:
            sat_names.append(tle_lines[i])
            new_lines.append(tle_lines[i])
            new_lines.append(tle_lines[i+1])
            new_lines.append(tle_lines[i+2])
    return new_lines

if __name__ == "__main__":
    
    unique_lines = []
    tles_dir_path = '/workspaces/ma-max-wendler/scripts/keplertraces/tles/examples_requested_at_2023-10-23-11-06-08/'
    print("filtering TLE lists from ", tles_dir_path, "...\n")
    
    tles_fnames = os.listdir(tles_dir_path)
    
    # find satnogs tle list to get walltime from filename
    try:
        satnogs_fname = [match for match in tles_fnames if match.startswith("satnogs_")][0]
    except: 
        IndexError("No SATNOGs constellation file starting with 'satnogs_' found.")

    try:
        starlink_fname = [match for match in tles_fnames if match.startswith("starlink_")][0]
    except:
        IndexError("No Starlink constellation file starting with 'starlink_' found.")

    try:
        oneweb_fname = [match for match in tles_fnames if match.startswith("oneweb_")][0]
    except:
        IndexError("No Oneweb constellation file starting with 'oneweb_' found.")

    try:
        iridiumnext_fname = [match for match in tles_fnames if match.startswith("iridiumNEXT_")][0]
    except:
        IndexError("No IridiumNEXT constellation file starting with 'iridiumNEXT_' found.")

    satnogs_tles_path = tles_dir_path + satnogs_fname
    starlink_tles_path = tles_dir_path + starlink_fname
    oneweb_tles_path = tles_dir_path + oneweb_fname
    iridiumnext_tles_path = tles_dir_path + iridiumnext_fname

    # get satnogs leo list, satnogs leo eccentric list
    with open(satnogs_tles_path, "r") as tles_f:
        unique_lines = filter_doubles(tles_f.readlines())
    satnogs_leo_lines, satnogs_eccentric_lines = filter_tles_leo_ecc(unique_lines)
    
    # filter Iridium and Starlink satellites from satnogs list to avoid cross-constellation doubles
    satnogs_leo_lines_filtered = []
    for i in range(0, len(satnogs_leo_lines), 3):
        if "IRIDIUM" not in satnogs_leo_lines[i] and "STARLINK" not in satnogs_leo_lines[i]:
            satnogs_leo_lines_filtered += satnogs_leo_lines[i:i+3]

    # don't get starlink eccentric lines, as the eccentric SHERPA-LTC2 is already contained in SATNOGs

    # flag old satnogs and cubesat tles list as invalid by adding "_" as name prefix
    os.rename(satnogs_tles_path, satnogs_tles_path.removesuffix(satnogs_fname) + "_" + satnogs_fname)

    # get wall time of average TLE epoch string for remaining satnogs satellites
    satnogs_avg_walltime = get_avg_epoch_str(satnogs_leo_lines_filtered)
    # write satnogs leo file
    with open(tles_dir_path + "satnogs_leo_" + satnogs_avg_walltime + ".txt", "w") as tles_f:
        tles_f.writelines(satnogs_leo_lines_filtered)
    
    print("filtered",
          int((len(satnogs_eccentric_lines) / 3 )),
          "eccentric LEO satellites overall")
    
    # Compile eccentric TLEs into one 'constellation' of TLEs. 
    eccentric_lines = [] + satnogs_eccentric_lines
    eccentric_avg_walltime = get_avg_epoch_str(eccentric_lines)
    with open(tles_dir_path + "eccentric_" + eccentric_avg_walltime + ".txt", "w") as tles_f:
        tles_f.writelines(eccentric_lines)
    
    # remove doubles from starlink, oneweb, iridium next
    for path in [starlink_tles_path, oneweb_tles_path, iridiumnext_tles_path]:
        with open(path, "r") as tles_f:
            unique_lines = filter_doubles(tles_f.readlines())
        
        avg_walltime = get_avg_epoch_str(unique_lines)
        
        os.rename(path, tles_dir_path + "_" + path.split("/")[-1])
        new_fname = path.split("/")[-1].split("_")[0] + "_" + avg_walltime + ".txt"

        with open(tles_dir_path + new_fname, "w") as tles_f:
            tles_f.writelines(unique_lines)