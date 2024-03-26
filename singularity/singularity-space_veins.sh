#!/bin/sh

#
# singularity-space_veins -- Singularity container for quickly building and running space_Veins simulations anywhere
# Copyright (C) 2020 Christoph Sommer <sommer@cms-labs.org>
# Copyright (C) 2022 Mario Franke <research@m-franke.net>
#
# Documentation for these modules is at http://veins.car2x.org/ or https://sat.car2x.org/
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

SCRIPTDIR=$(dirname "$0")
SCRIPTSTEM=$(basename -s .sh "$0")

singularity run -H work:/work -C --net --network none "${SCRIPTDIR}/${SCRIPTSTEM}.sif" --launchd --chdir "$@"
