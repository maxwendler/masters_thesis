//
// Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>
//
//
// SPDX-License-Identifier: GPL-2.0-or-later
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#pragma once

#include <tuple>
#include <math.h>
#include <stdexcept>
#include "veins/base/utils/Coord.h"

namespace space_veins
{
    class PolarCoordinates
    {   
        public:
            // in interval [0,pi]
            double polarAngle;
            // in interval [0,2*pi)
            double azimuth;
            // in km
            double radius;

            PolarCoordinates(double polarAngle, double azimuth, double radius) : radius(radius) 
            {
                if (polarAngle < 0 || polarAngle > M_PI)
                {
                    throw std::invalid_argument("'polarAngle' must be in interval 0 <= i <= pi");
                }
                else {
                    this->polarAngle = polarAngle;
                }
                if (azimuth < 0 || azimuth >= 2*M_PI)
                {
                    throw std::invalid_argument("'azimuth' must be in interval 0 <= a < 2*pi");
                }
                else
                {
                    this->azimuth = azimuth;
                }
            }

            PolarCoordinates(std::tuple<double,double,double> cartesianCoords)
            {
                double x = std::get<0>(cartesianCoords);
                double y = std::get<1>(cartesianCoords);
                double z = std::get<2>(cartesianCoords);
                
                radius = sqrt(pow(x,2) + pow(y,2) + pow(z,2));
                polarAngle = acos(z / radius);
                azimuth = atan2(y, x);
                if (azimuth < 0)
                {
                    azimuth = 2* M_PI + azimuth;
                }
            }

            veins::Coord getCartesianCoords() const {
                // Conversion according to https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates.
                float x = radius * sin(polarAngle) * cos(azimuth);
                float y = radius * sin(polarAngle) * sin(azimuth);
                float z = radius * cos(polarAngle);
                return veins::Coord(x,y,z);
            }   
    };
}