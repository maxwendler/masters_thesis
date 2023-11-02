import argparse
from parseomnetini import parseomnetini
from tleparse import parse
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
import astropy.coordinates as coords
from timeit import default_timer as timer
import os

start_t = timer()

parser = argparse.ArgumentParser(prog="create_traces.py", description="Creates a .txt file with a satellite movement trace for each TLE in the given file; written to the given output directory.")

parser.add_argument('omnetinipath', help="Path of omnetpp.ini that has settings for 'sim-time-limit', '*.leo*[*].mobility.updateInterval' and '*.satelliteInserter.wall_clock_sim_start_time_utc'.")
parser.add_argument('tlespath', help="Path of .txt with list of TLEs for which to create traces.")
parser.add_argument('outputdir', help="Path of directory where .trace files (.txt-like contents) with satellite traces will be written to; one file per satellite.")
parser.add_argument('-c','--config', help='Specifies configuration in omnetpp.ini of which values shall overwrite general settings.')

args = parser.parse_args()
if not str(args.outputdir).endswith("/"):
    args.outputdir += "/"
args.outputdir += args.tlespath.split("/")[-1].removesuffix(".txt") + "/"

# create outputdir if it does not exist
try:
    os.makedirs(args.outputdir)
except:
    pass

# get trace parameters (duration = sim-time-limit, spacing = updateInterval) from omnetpp.ini at given path
timelimit, updateInterval, startTime = parseomnetini(args.omnetinipath, args.config)
periods = int(timelimit / updateInterval)

print(f"startTime {startTime}")

omnetparse_t = timer()
print(f"Time for parsing omnetpp.ini: {omnetparse_t-start_t} seconds")

# create inputs for poliastro Kepler model from tles in file at given path
inputs = parse(args.tlespath)

kepler_inputs_t = timer()
print(f"Time for creating kepler inputs: {kepler_inputs_t - omnetparse_t} seconds")

# create and write traces; one file per satellite
for kepler_inputs in inputs:
    # satellites will be renamed if name contains "/", to not mess up resulting paths
    output_path = args.outputdir + kepler_inputs.name.replace("/","-") + ".trace"
    
    orb = Orbit.from_classical(
            Earth, 
            a=kepler_inputs.semimajoraxis, 
            ecc=kepler_inputs.ecc, 
            inc=kepler_inputs.inc, 
            raan=kepler_inputs.raan, 
            argp=kepler_inputs.argp, 
            nu=kepler_inputs.true_anom, 
            epoch=kepler_inputs.epoch)
    ephem = orb.to_ephem(strategy=EpochsArray(epochs=time_range(startTime, spacing=updateInterval, periods=periods)))
    
    cartesian_trace = ephem.sample(ephem.epochs)
    skycoord = coords.SkyCoord(coords.TEME(cartesian_trace, obstime=ephem.epochs), frame="teme", obstime=ephem.epochs).transform_to("itrs")
    skycoord.representation_type = coords.WGS84GeodeticRepresentation
    print(skycoord)
    wgs84_trace = skycoord.frame.cache["representation"][('WGS84GeodeticRepresentation', True)]
    
    with open(output_path, "w") as trace_f:
        trace_f.write(kepler_inputs.name)
        for coord in wgs84_trace:
            trace_f.write("\n" + str(coord.lon.value) + "," + str(coord.lat.value) + "," + str(coord.height.value))

    print("Wrote a trace...")  

print(f"Successfully wrote traces to {args.outputdir}!")

end_t = timer()
print(f"Time for creating traces: {end_t - kepler_inputs_t} seconds")
print(f"Execution of the script with the provided arguments took {end_t - start_t} seconds.")