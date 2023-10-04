import argparse
from parseomnetini import parseomnetini
from tleparse import parse

parser = argparse.ArgumentParser(prog="placeholder name", description="placeholder description")

parser.add_argument('omnetinipath', help="Path of omnetpp.ini that has settings for 'sim-time-limit' and '*.leo*[*].mobility.updateInterval'")
parser.add_argument('tlespath', help="Path of .txt with list of TLEs for which to create traces.")
parser.add_argument('-c','--config', help='Specifies configuration in omnetpp.ini of which values shall overwrite general settings for "sim-time-limit" and "*.leo*[*].mobility.updateInterval"')

args = parser.parse_args()

# get trace parameters (duration = sim-time-limit, spacing = updateInterval) from omnetpp.ini at given path
timelimit, updateInterval = parseomnetini(args.omnetinipath, args.config)

# create inputs for poliastro Kepler model from tles in file at given path
inputs = parse(args.tlespath)