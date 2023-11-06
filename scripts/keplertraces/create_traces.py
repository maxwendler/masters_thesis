import argparse
from parseomnetini import parseomnetini
from tleparse import parse_orbits
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
import astropy.coordinates as coords
import astropy.units as u
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
timelimit, update_interval, start_time = parseomnetini(args.omnetinipath, args.config)
periods = int(timelimit / update_interval)

print(f"startTime {start_time}")

omnetparse_t = timer()
print(f"Time for parsing omnetpp.ini: {omnetparse_t-start_t} seconds")

# create inputs for poliastro Kepler model from tles in file at given path
named_orbits = parse_orbits(args.tlespath)

orbits_t = timer()
print(f"Time for creating poliastro orbits: {orbits_t - omnetparse_t} seconds")

# create and write traces; one file per satellite
for name_orbit_tuple in named_orbits:
    # satellites will be renamed if name contains "/", to not mess up resulting paths
    output_path = args.outputdir + name_orbit_tuple[0].replace("/","-") + ".trace"
    
    orb = name_orbit_tuple[1]
    ephem = orb.to_ephem(strategy=EpochsArray(epochs=time_range(start_time, spacing=update_interval, periods=periods)))
    
    cartesian_trace = ephem.sample(ephem.epochs)
    grcs_trace = coords.SkyCoord(coords.GCRS(cartesian_trace, obstime=ephem.epochs), frame="gcrs", obstime=ephem.epochs)
    itrs_trace = grcs_trace.transform_to(coords.ITRS) 
    wgs84_trace = itrs_trace.spherical.represent_as(coords.WGS84GeodeticRepresentation)
    
    wgs84_trace_in_deg = [(coord.lon.to(u.deg), coord.lat.to(u.deg), coord.height) for coord in wgs84_trace]
    
    with open(output_path, "w") as trace_f:
        trace_f.write(name_orbit_tuple[0])
        for coord in wgs84_trace_in_deg:
            trace_f.write("\n" + str(coord[0].value) + "," + str(coord[1].value) + "," + str(coord[2].value))

    print("Wrote a trace...")  

print(f"Successfully wrote traces to {args.outputdir}!")

end_t = timer()
print(f"Time for creating traces: {end_t - orbits_t} seconds")
print(f"Execution of the script with the provided arguments took {end_t - start_t} seconds.")