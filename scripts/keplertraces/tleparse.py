from tletools import TLE
from keplerinputs import KeplerInputs
from astropy.time import Time
from datetime import datetime

def remove_empty_startend_lines(orig_lines: list[str]) -> list[str]:
    """ removes empty lines at start and end of TLE file, which are allowed but must be removed """

    line_range = range(0, len(orig_lines))
    
    first_non_empty = 0
    for i in line_range:
        if orig_lines[i] != "\n":
            first_non_empty = i
            break 

    last_non_empty = 0
    for i in reversed(line_range):
        if orig_lines[i] != "\n":
            last_non_empty = i
            break
    
    return orig_lines[first_non_empty : last_non_empty+1]

def read(path: str) -> list[TLE]:
    """ 
    reads TLEs file at 'path' and creates TLE objects from TLE-tools API,
    see https://pypi.org/project/TLE-tools/  
    """

    content_lines = []
    with open(path, "r") as f:
        content_lines = remove_empty_startend_lines(f.readlines())

    tles = []
    for i in range(0, len(content_lines), 3):
        tle_lines = content_lines[i:i+3]
        try:
            tles.append(TLE.from_lines(*tle_lines))
        except Exception as ex:
            print(ex.args)
            raise ValueError("Incorrect format of TLEs file: Does not consist of line triples, each representing a TLE.")

    return tles

""" lambda method that creates KeplerInputs instance from TLE-tools' TLE instance"""
TLE_TO_KI = lambda tle: KeplerInputs(tle.name, tle.ecc, tle.inc, tle.raan, tle.argp, mean_anom=tle.M, mean_motion=tle.n, epoch=tle.epoch)

def parse(path: str) -> list[KeplerInputs]:
    """ 
    reads TLEs file at 'path' and parses contained TLEs to inputs for the Kepler model,
    see `kepler.keplerinputs.KeplerInputs`
    """
    tles = read(path)
    results = list(map(TLE_TO_KI, tles))
    print(f"parsed {len(results)} TLEs")
    return results

def get_avg_epoch_str(tles_as_lines: str) -> str:
    epoch_sum = 0
    for i in range(0, len(tles_as_lines), 3):
        tle = TLE.from_lines(tles_as_lines[i], tles_as_lines[i+1], tles_as_lines[i+2])
        epoch = tle.epoch
        epoch.format = 'unix'
        epoch_sum += epoch.value
    
    avg_epoch_unix = epoch_sum / int(len(tles_as_lines) / 3)
    avg_epoch_time = Time(avg_epoch_unix, format='unix' ,scale='utc')
    epoch_sum = 0
    for i in range(0, len(tles_as_lines), 3):
        tle = TLE.from_lines(tles_as_lines[i], tles_as_lines[i+1], tles_as_lines[i+2])
        epoch = tle.epoch
        epoch.format = 'unix'
        epoch_sum += epoch.value
    
    avg_epoch_unix = epoch_sum / int(len(tles_as_lines) / 3)
    avg_epoch_time = Time(avg_epoch_unix, format='unix' ,scale='utc')
    avg_epoch_time.format = 'datetime'
    avg_epoch_dt_str = avg_epoch_time.value.strftime("%Y-%m-%d-%H-%M-%S")
    
    return avg_epoch_dt_str