# General
- The whole code assumes simulation time steps / satellite update intervals of 1 second and requires changes for flexibility w.r.t. the time steps.

# Docker (devcontainer) and Singularity setup
- implement use of a pip-requirements.txt similar to the conda-requirements.txt file for setting up packages which can be installed exlusively with pip; instead of direct specification of tle-tools package in use-pip-in-conda-env.sh and Snakefile
- => enables modular use of further pip-exclusive packages if required 
- => needs to happen activated conda environment !
- (maybe: find solution to implement conda installation and pip installation via Dockerfile instead of postCreateCommand in devcontainer.json, so it actually is part of the Docker container, and not Docker container as VSCode devcontainer)
- conda is actually only required for orekit GCRS->ITRF transformation in trace creation. Hence, evaluate if packages currently installed in conda environment could be installed in container setup, to avoid installation of certain packages in conda environment again. Still, pip TLE-tools installation should happen in conda environment. 

# examples/space_veins/Snakefile and [...] smk.config.yaml
- enable use of VSCode devcontainer by implementing a way for shell directives of rules to not execute 'cd examples/space_veins' when not run in Singularity container.
- add flexibility to use debug configurations to all rules, currently only implemented for some; e.g. "run"
- implement rules to evaluate if relevant parameters for Keplerian/SGP4/Circular model and trace creation in omnetpp.ini have changes, and avoid reexecution if it is not the case. Currently, any change of the omnetpp.ini prompts reexecution of all simulations, metrics calculation and plotting. 
- implement creation of superconstellation data by combining subconstellation data everywhere; currently only exists for merging of coordinate CSVs
- rules creating plots as .svg and .html: Evaluate if only one format is required and other can be removed => adapt used Python scripts accordingly
- calculate memory limits for coord CSV creation in config dynamically from scaling factor and simulation time limit; currently they are not up to date with the configured simulation time. They can be (over)estimated using the console output of opp_vec2csv.pl in the vec2csv rule.
- implement rule to request runtime results of all currently configured constellations, i.e. the ones from get_composed_constellations
- if simulation warmup period should be flexibly configurable: add as smk.config.yaml parameter and use it in rule 'vec2csv', also adapt other rules where "15" is currently statically configured
- rule 'vec2csv': make vec_file parameter work flexibly to enable adding of new named parameters in the omnetpp.ini
- implement surface location independence of TEME and ITRF coordinate results (w.r.t. lines 436-498), and average SGP4 radii for circular model (The following lines.)
- rule plot_diff_distributions: implement different output path in stats/ directory for JSON data output; requires adaptation of the used Python script 
- rule plot_extrema_zs: 
    - implement different output path in stats/ directory for .txt data output; requires adaptation of the used Python script
    - implement option to only plot extrema for a specified satellite module => already supported by the used Python script 
- all rules with "diffs_or_changes" option w.r.t. to output: find clearer names for which variant uses absolute values and which doesn't => adapt used Python scripts

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

## scripts/keplertraces/updateomnetini.py, Snakemake workflow and road network files 
- create road network files for all locations
- create configurations for all locations in omnetpp.ini, which avoids rerunning the whole Snakemake workflow when changing the location and consequently the omnetpp.ini 
- => scripts/utility/update_nod_xml.py, examples/space_veins/two-nodes.nod.xml.template and Snakemake rules update_nod_xml, update_net_xml not required anymore 
- might be necessary for new constellations: implement ordering of paths for get_avg_sgp4_radii to match configurations created by update_omnetini. Currently, matches order of get_tle_paths and hence works.

## scripts/utility/compose_pos_csv.py
- reduce buffer memory by individually reading and immediately writing csv lines

## scripts/statistics/runtime_from_benchmarks.py
- use CPU time instead of simply time (CPU time were added manually for thesis)

## scripts/plots/plot_orbs.py
 - change csv_paths and output_path from optional to positional arguments => update Snakemake rule accordingly

## scripts/plots/plot_differences.py
- optionally: if ecdf plots deemed relevant, enable plotting of circular and keplerian deviations in one ecdf plot next 
  to one positional deviation plot; or separate ecdf plotting into new script => adapt rules "plot_kepler_circular_pos_diff_diffs" and "plot_kepler_and_circular_pos_diff" to support these options

## scripts/statistics/diff_differences.py
- don't parse second CSV of comparison completely to dict, but parse each line individually and compare + directly create output line, to save memory load

## scripts/plots/plot_const_diff_extrema_positions.py
- optimize runtime by
    - solution for not traversing positional difference csv of constellation again and again for each module, i.e. optimize module difference lookup
    - solution for not traversing coordinate csv of constellation again and again for each module, i.e. optimize module coordinates lookup
- optimize memory load by only saving module coordinates for the extrema times during module coordinates lookup
- implement solution to also identify smaller extrema occuring for the Keplerian model

## scripts/statistics/sop_stats.py
- optimize memory load by directly writing calculated data to CSVs instead of collecting all the data first

## scripts/statistics/plot_sop_stats.py
- find solution to add annotation text to minimum elevation angle annotation which does not shift subplots, or add that annotation elsewhere

## scripts/statistics/all_interval_changes.py
- improve runtime so that it can actually be used => enable use in available_sats_diffs Snakemake rule and script

## scripts/statistics/aligned_period_sop_stat_differences.py
- split into (1) script to calculate aligned differences and (2) script to plot these results (currently, behavior determined by existance of --plot or --json option)

## scripts/plots/plot_const_aligned_sop_stats_at_offset.py
- find a solution to not have overlapping annotations for satellite module names of points in plot, or remove the currently commented code for this

## scripts/plots/plot_anglegroup_sop_stats_at_offset.py
- find a solution to not have overlapping annotations for satellite module names of points in plot, or remove the currently commented code for this
- either plot average or maximum values, not both as currently => adapt according Snakemake rule if choice between options shall be allowed

## scripts/statistics/sat_period_zenith_interval_changes.py
- exclude period pairs where one period lies before, one after epoch, to limit comparisons to only inter-backward and inter-forward propagation

## scripts/plots/plot_zenith_interval_diff_to_offset_diff.py
- dynamic outliers for line fit (currently set to fixed number 0)

## scripts/plots/plot_const_period_zenith_shifts.py
- separate line fit for forward/backward propagation
- find a solution to not have overlapping annotations for satellite module names of points in plot, or remove the currently commented code for this

# src/

## src/space_veins/modules/mobility/{Circular,Kepler}Mobility and [...]/SatelliteInserter
- there might be uneccesary includes in the files of those directories

## src/space_veins/modules/mobility/CircularMobility and Snakemake workflow
 - ensure that SGP4 simulation of orbits of TLEs file is always run before circular simulation, and average radii are calculated, so that SGP4 can be fully removed from CircularMobility classes - currently provides radii if no average radius is given
 - => .ned parameters of SatelliteInserter and Snakemake configuration variable use_avg_sgp4_radii not required anymore too

## src/space_veins/modules/mobility/CircularMobility/CirclePlane.cc
 - remove cross-product step in circle plane (i.e. plane of circular orbit) unit vector calculation during init.