# General
- The whole code assumes simulation time steps / satellite update intervals of 1 second and requires changes for flexibility w.r.t. the time steps.

# scripts/

## scripts/keplertraces/create_traces.py
- replace optional configuration of (1) ITRF ouput (2) using Orekit for GCRS to ITRF conversion with static configuration
- add finished traces count as progress console output
- implement potential parallel processing of TLEs of a file

## scripts/keplertraces/before_median_start_time.ipynb, scripts/keplertraces/tlefilter.py
- instead of calculating start time from median in notebook, replace file naming in tlefilter.py after average epoch of the TLEs with the half time before median calculation; then examples/space_veins/tles/avg_epoch_timestamps can be deleted
- use simulation time from snakemake configuration for that instead of current static value
- add removal of eccentric TLEs from Starlink, i.e. for SHERPA-LTC2, which was removed manually

## scripts/keplertraces/tletimes.py and subsequent uses of examples/space_veins/tles/*_times.json files
- replace "offset_to_start" with clearer "seconds to epoch", requires adaptation of scripts using the *_times.json files

## scripts/utility/compose_pos_csv.py
- reduce buffer memory by individually reading and immediately writing csv lines

# src/

## src/space_veins/modules/mobility/CircularMobility and Snakemake workflow
 - ensure that SGP4 simulation of orbits of TLEs file is always run before circular simulation, and average radii are calculated, so that SGP4 can be fully removed from CircularMobility classes - currently provides radii if no average radius is given

## src/space_veins/modules/mobility/CircularMobility/CirclePlane.cc
 - remove cross-product step in circle plane (i.e. plane of circular orbit) unit vector calculation during init.