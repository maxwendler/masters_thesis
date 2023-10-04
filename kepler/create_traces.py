import argparse
from parseomnetini import parseomnetini
from tleparse import parse
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
import astropy.coordinates as coords
from timeit import default_timer as timer

start_t = timer()

TRACE_CSV_SEPARATOR = ";"

parser = argparse.ArgumentParser(prog="placeholder name", description="placeholder description")

parser.add_argument('omnetinipath', help="Path of omnetpp.ini that has settings for 'sim-time-limit' and '*.leo*[*].mobility.updateInterval'")
parser.add_argument('tlespath', help="Path of .txt with list of TLEs for which to create traces.")
parser.add_argument('outputpath', help="Path of .csv where created traces will be written to.")
parser.add_argument('-c','--config', help='Specifies configuration in omnetpp.ini of which values shall overwrite general settings for "sim-time-limit" and "*.leo*[*].mobility.updateInterval"')

args = parser.parse_args()

# get trace parameters (duration = sim-time-limit, spacing = updateInterval) from omnetpp.ini at given path
timelimit, updateInterval = parseomnetini(args.omnetinipath, args.config)
periods = int(timelimit / updateInterval)

# create inputs for poliastro Kepler model from tles in file at given path
inputs = parse(args.tlespath)

# create and write traces
with open(args.outputpath, "w") as traces_file:
    
    for kepler_inputs in inputs:
        orb = Orbit.from_classical(
            Earth, 
            a=kepler_inputs.semimajoraxis, 
            ecc=kepler_inputs.ecc, 
            inc=kepler_inputs.inc, 
            raan=kepler_inputs.raan, 
            argp=kepler_inputs.argp, 
            nu=kepler_inputs.true_anom, 
            epoch=kepler_inputs.epoch)

        ephem = orb.to_ephem(strategy=EpochsArray(epochs=time_range(kepler_inputs.epoch, spacing=updateInterval, periods=periods)))
        cartesian_trace = ephem.sample(ephem.epochs)
        WGS84_trace = list(map(lambda cart_rep: coords.WGS84GeodeticRepresentation.from_cartesian(cart_rep) , cartesian_trace))

        trace_str = kepler_inputs.name
        for coord in WGS84_trace:
            trace_str += TRACE_CSV_SEPARATOR + str(coord.lon.value) + "," + str(coord.lat.value) + "," + str(coord.height.value)

        traces_file.write(trace_str + "\n")

print(f"Successfully wrote traces to {args.outputpath}!")

end_t = timer()
print(f"Execution of the script with the provided arguments took {end_t - start_t} seconds.")