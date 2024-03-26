# Copyright (C) 2023 Mario Franke

# SPDX-License-Identifier: GPL-2.0-or-later

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import math
import argparse

parser = argparse.ArgumentParser(description='Calculate the minimum and maximum beam radius given satellite height on zenith, beam width in deg, and minimum elevation angle.')
parser.add_argument('height', metavar='HEIGHT', type=float, help='Satellite height in km at Zenith over reference point.')
parser.add_argument('bwidth', metavar='WIDTH', type=float, help='Satellite beam width in degree.')
parser.add_argument('minimumElevation', metavar='ELEVATION', type=float, help='Minimum elevation angle such that ground stations and satellites can communicate.')

args = parser.parse_args()

beamWidthHalf = math.radians(args.bwidth / 2.0)
alpha = math.radians(180 - (180 - args.minimumElevation) - (args.bwidth / 2.0))

minHypo = args.height / math.cos(beamWidthHalf)
minRadius = math.sin(beamWidthHalf) * minHypo
print("minRadius: %.2f km" % minRadius)

minEleHypo = args.height / math.cos(math.radians(90.0 - args.minimumElevation))
maxHypo = args.height / math.sin(alpha)
smallA = math.cos(math.radians(args.minimumElevation)) * minEleHypo
largeA = math.cos(alpha) * maxHypo
maxRadius = largeA - smallA
print("maxRadius: %.2f km" % maxRadius)