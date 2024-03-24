"""
Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from math import pi
import astropy.units as u
from astropy.time import Time
from astropy.constants import GM_earth
from poliastro.twobody.angles import M_to_E, E_to_nu

SECONDS_IN_DAY = 86400

class KeplerInputs:
    """
    Class holding the inputs for poliastro's `poliastro.twobody.orbit.scalar.Orbit.from_classical` method,
    see: https://docs.poliastro.space/en/stable/autoapi/poliastro/twobody/orbit/scalar/index.html,
    where 'a' is called 'semimajoraxis' here, 'nu' is called 'semimajoraxis'

    Of the input parameters, only epoch needs to be an instance of `astropy.time.core.Time`, the other can be numbers.
    They will be converted to instances of `astropy.units.Quantity` in `__init__`.
    """

    def __init__(self, 
                 name:str,
                 ecc: float, 
                 inc: float, 
                 raan: float, 
                 argp: float, 
                 mean_anom: float, 
                 mean_motion: float, 
                 epoch: Time):
        
        self.name = name
        self.ecc = u.Quantity(ecc, unit=u.one)
        self.inc = u.Quantity(inc, unit=u.deg)
        self.raan = u.Quantity(raan, unit=u.deg)
        self.argp = u.Quantity(argp, unit=u.deg)
        self.epoch = epoch

        # Conversion via methods of poliastro, 
        # see https://docs.poliastro.space/en/stable/autoapi/poliastro/twobody/angles/index.html 
        self.true_anom =  E_to_nu( M_to_E( u.Quantity(mean_anom, unit=u.deg), self.ecc ), self.ecc )
        
        # calculation according to "Textbook on spherical astronomy", p.108
        # where n**2 * a**3 = GM, i.e. n = (GM/n**2)**(1/3),
        # which can also be expressed as (GM*time_per_revolution**2/(4*pi*pi)) with 
        # n = 2pi / time_per_revoltion according to "Fundamental planetary science", p.30
        # (1/TLE's mean motion) would be 'days per revolution', hence * SECONDS_IN_A_DAY
        secs_per_revolution = SECONDS_IN_DAY / mean_motion 
        self.semimajoraxis = u.Quantity((secs_per_revolution**2 * GM_earth.value / (4 * pi**2) )**(1/3) / 1000, unit=u.km)

    def __str__(self) -> str:
        output = "Inputs for kepler model of satellite: " + self.name + "\n"
        output += "ecc: " + str(self.ecc) + "\n"
        output += "inc: " + str(self.inc) + "\n"
        output += "raan: " + str(self.raan) + "\n"
        output += "argp: " + str(self.argp) + "\n"
        output += "true_anom: " + str(self.true_anom) + "\n"
        output += "semimajoraxis " + str(self.semimajoraxis)

        return output