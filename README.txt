An extension of space_Veins - itself an extension for Veins simulating 
Vehicle-to-Satellite Communication - with two new models for satellite mobility,
the KeplerianMobility (based on laws of Kepler and Newton describing the two-body problem),
and the CircularMobility, which approximates all orbits as circular ones. 
This repository also contains a Snakemake workflow to analyze and compare the models,
which is documented in the Snakefile in examples/space_veins, including details on
the use of the applied python scripts in scripts/utility, scripts/keplertraces,
scripts/statistics and scripts/plots. Background and results of this analysis are
documented in thesis.pdf of the according Master's thesis. If you don't want to 
manage dependencies yourself, the Snakemake worflow requires the use of the Singularity container provided 
with this repository. The Singularity setup can be executedby running the Snakemake 
rules "buildContainer" and "finish_dep_setup" (including the "--use-singularity" option) 
in examples/space_veins. 

space_Veins and this extension is composed of many parts. See the version control 
log for a full list of contributors and modifications. Each part is protected by 
its own, individual copyright(s), but can be redistributed and/or modified under 
an open source license. License terms are available at the top of each file. Parts 
that do not explicitly include license text shall be assumed to be governed by the 
"GNU General Public License" as published by the Free Software Foundation -- either
version 2 of the License, or (at your option) any later version
(SPDX-License-Id: GPL-2.0-or-later). Parts that are not source code and
do not include license text shall be assumed to allow the Creative Commons
"Attribution-ShareAlike 4.0 International License" as an additional option
(SPDX-License-Id: GPL-2.0-or-later OR CC-BY-SA-4.0). Full license texts
are available with the source distribution. 

TLE data was obtained from Celestrak (https://celestrak.org/NORAD/elements/) and is license-free.
The TLE files in examples/space_veins/tles were edited as described in section 5.1 of the thesis PDF.