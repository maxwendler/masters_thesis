import argparse
from parseomnetini import parseomnetini
from tleparse import parse_orbits
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
import astropy.coordinates as coords
import astropy.units as u
from timeit import default_timer as timer
import os
from orekit.pyhelpers import download_orekit_data_curdir, setup_orekit_curdir
import sys 
sys.path.append(os.path.join(sys.path[0],"..",".."))
from scripts.utility.satname_to_modname import satname_to_modname
import json
from pathlib import Path
from astropy.time import Time
from parseomnetini import parseomnetini

start_t = timer()

parser = argparse.ArgumentParser(prog="create_traces.py", description="Creates a .txt file with a satellite movement trace for each TLE in the given file; written to the given output directory.")

parser.add_argument('ini_path', help="Path omnetpp.ini with 'sim-time-limit', '*.leo*[*].mobility.updateInterval' and '*.satelliteInserter.wall_clock_sim_start_time_utc'. values assigned.")
parser.add_argument('tlespath', help="Path of .txt with list of TLEs for which to create traces.")
parser.add_argument('outputdir', help="Path of directory where .trace files (.txt-like contents) with satellite traces will be written to; one file per satellite.")
parser.add_argument('-c','--config', help='Specifies configuration in omnetpp.ini of which values shall overwrite general settings.')
parser.add_argument('-i', '--itrf', action='store_true', help='Outputs traces in ITRS/ITRF traces instead of WGS84.')
parser.add_argument('-o', '--orekit', action='store_true', help='Creates traces via orekit instead of poliastro/astropy APIs.')

args = parser.parse_args()
if not str(args.outputdir).endswith("/"):
    args.outputdir += "/"
args.outputdir += args.tlespath.split("/")[-1].removesuffix(".txt") + "/"

# create outputdir if it does not exist
try:
    os.makedirs(args.outputdir)
except:
    pass

if args.itrf:
    print("Creating traces in ITRF...")
else:
    print("Creating traces in WGS84...")

if args.orekit:
    print("Using orekit API for GCRS to ITRF conversion...")
    if "orekit-data.zip" not in os.listdir("./"):
        download_orekit_data_curdir()
    
    import orekit
    vm = orekit.initVM()
    print ('Java version:',vm.java_version)
    print ('Orekit version:', orekit.VERSION)

    setup_orekit_curdir()

    from org.orekit.frames import FramesFactory, ITRFVersion
    from org.orekit.utils import IERSConventions
    from org.orekit.time import AbsoluteDate, DateTimeComponents, TimeScalesFactory
    from org.orekit.utils import PVCoordinates
    from org.hipparchus.geometry.euclidean.threed import Vector3D
else:
    print("Using astropy GCRS to ITRF conversion...")

timelimit, update_interval, start_time = parseomnetini(args.ini_path, args.config)

periods = int(timelimit / update_interval)

print(f"startTime {start_time}")
print(f"updateInterval {update_interval}")
print(f"timelimit {timelimit}")

omnetparse_t = timer()
print(f"Time for parsing omnetpp.ini: {omnetparse_t-start_t} seconds")

# create inputs for poliastro Kepler model from tles in file at given path
named_orbits = parse_orbits(args.tlespath)

orbits_t = timer()
print(f"Time for creating poliastro orbits: {orbits_t - omnetparse_t} seconds")

two_pi_to_negpos_pi_range = lambda deg_val: (-360 << u.deg) + deg_val if deg_val > (180 << u.deg) else deg_val

modname_to_satname_dict = {}

# create and write traces; one file per satellite
for name_orbit_tuple in named_orbits:
    # satellites will be renamed if name contains "/", to not mess up resulting paths
    satname = name_orbit_tuple[0].replace("/","-")
    leo_modname = satname_to_modname(satname)
    modname_to_satname_dict[leo_modname] = satname
    output_path = args.outputdir + satname  + ".trace"
    
    orb = name_orbit_tuple[1]
    ephem = orb.to_ephem(strategy=EpochsArray(epochs=time_range(start_time + update_interval, spacing=update_interval, periods=periods)))
    
    cartesian_trace = ephem.sample(ephem.epochs)
    if not args.orekit:
        grcs_trace = coords.SkyCoord(coords.GCRS(cartesian_trace, obstime=ephem.epochs), frame="gcrs", obstime=ephem.epochs)
    
    if args.orekit:

        utc = TimeScalesFactory.getUTC()
        gcrf = FramesFactory.getGCRF()
        itrf = FramesFactory.getITRF(ITRFVersion.ITRF_2008 ,IERSConventions.IERS_2010, False)

        itrf_trace = []
        for i in range(0, len(ephem.epochs)):
            epoch = ephem.epochs[i]
            epoch.format = "isot"

            datetime_components = DateTimeComponents.parseDateTime(epoch.value)
            date = AbsoluteDate(datetime_components, utc)
            
            cartesian_coord = cartesian_trace[i]
            gcrs_coord = PVCoordinates(Vector3D(float(cartesian_coord.x.value),float(cartesian_coord.y.value),float(cartesian_coord.z.value)))
            gcrfItrfTransformation = gcrf.getTransformTo(itrf, date)
            itrf_trace.append(gcrfItrfTransformation.transformPVCoordinates(gcrs_coord).getPosition())
    else:
        itrf_trace = grcs_trace.transform_to(coords.ITRS)

    if not args.itrf:
        if args.orekit:
            x_array = [ (coord.getX() << (u.km)) for coord in itrf_trace]
            y_array = [ (coord.getY() << (u.km)) for coord in itrf_trace]
            z_array = [ (coord.getZ() << (u.km)) for coord in itrf_trace]
            itrf_trace = coords.SkyCoord(x=x_array, y=y_array, z=z_array, frame="itrs", obstime=ephem.epochs)
        wgs84_trace = itrf_trace.spherical.represent_as(coords.WGS84GeodeticRepresentation)
        wgs84_trace_in_deg = [( two_pi_to_negpos_pi_range(coord.lat.to(u.deg)), 
                                two_pi_to_negpos_pi_range(coord.lon.to(u.deg)), 
                                coord.height) 
                                for coord in wgs84_trace]
    
    with open(output_path, "w") as trace_f:
        trace_f.write(satname)
        if args.itrf:
            if args.orekit:
                for coord in itrf_trace:
                    trace_f.write("\n" + str(coord.getX()) + "," + str(coord.getY()) + "," + str(coord.getZ()))
            else:
                for coord in itrf_trace:
                    trace_f.write("\n" + str(coord.x.value) + "," + str(coord.y.value) + "," + str(coord.z.value))
        else:
            for coord in wgs84_trace_in_deg:
                trace_f.write("\n" + str(coord[0].value) + "," + str(coord[1].value) + "," + str(coord[2].value))

    print("Wrote a trace...")  

with open(args.outputdir + "modname_to_satname_dict.json", "w") as dict_f:
    json.dump(modname_to_satname_dict, dict_f)

print(f"Successfully wrote traces to {args.outputdir}!")

end_t = timer()
print(f"Time for creating traces: {end_t - orbits_t} seconds")
print(f"Execution of the script with the provided arguments took {end_t - start_t} seconds.")