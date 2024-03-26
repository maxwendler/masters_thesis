<!--
SPDX-FileCopyrightText: 
2023 Mario Franke <research@m-franke.net>
2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later
-->

## space_Veins Example

This simulation requires to source the setenv file in the space_Veins root directory:
```
cd ../../
source setenv
cd examples/space_veins
```

If you want to use the configuration using veins_launchd, you have to start it first:
```
python3 ../../lib/veins/bin/veins_launchd -vv
```

Now you can run the example simulation:
```
./run -u Qtenv
```

## Snakemake workflow in Snakefile
For information on Snakemake, refer to the [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/): The Snakefile separates the workflow in the following parts, which are further documented in the Snakefile itself:
 0. Functions to read data from the Snakemake configuration in the right format.
 1. Rules of the singularity container.
 2. Rules to finish dependency setup in Singularity container, or VS devcontainer. For the latter, the conda setup is already performed on container creation.
 3. Rules for ITRF trace creation and running the OMNeT++ simulations.
 4. Rules to calculate runtime from Snakemake benchmarks. Note that sometimes the Snakemake benchmarks output strange results and should be checked individually, sometimes requiring rerunning.
 5. Rules for extracting coordinate data from OMNeT++ *.vec result files.
 6. Rules for calculating average SGP4 radii for circular model.
 7. Rules to plot orbits as interactive 3D plots.
 8. Rules to calculate and plot positional deviations between models.
 9. Rules to calculate and plot elevation angle, distance, propagation delay to SOP.
 10. Rules to calculate and plot communication/availability periods w.r.t. SOP.
 11. Rules to calculate overall time of different kinds of availability w.r.t. the SOP, summarizing individual communication/availability periods.

Many shell parts of the rules run Python scripts with bash -i -c 'python3 [...]' so that the conda environment is activated in the Singularity conatiner, which otherwise does not happen. The singularity container opens in the top directory of this repository, hence many shell directives start with 'cd examples/space_veins'. Rules should be generally run with the "--use-singularity" option or a snakemake profile (like "--profile smk.nsm.profile") which specifies this option. 