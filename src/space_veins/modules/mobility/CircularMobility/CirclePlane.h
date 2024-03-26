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
#include "veins/base/utils/Coord.h"
#include "space_veins/modules/mobility/CircularMobility/PolarCoordinates.h"

namespace space_veins 
{   
    class CirclePlane
    {   
        struct Cartesian2dInPlane
        {
            veins::Coord unitXVector, unitYVector;
        };

        public:
            const veins::Coord inPoint1;
            const veins::Coord inPoint2;

            const double radius;
            const double angularVelocityPerSecRad;
            const double startRadOffset;

            Cartesian2dInPlane cartesian2dSystem;
            
            CirclePlane():radius(0),angularVelocityPerSecRad(0),startRadOffset(0){};
            CirclePlane(veins::Coord point1, veins::Coord point2, double radius, double angularVelocityPerSecRad, double startRadOffset);
            CirclePlane& operator=(const CirclePlane& other);

            veins::Coord getPointAtSecond(double t);

        protected:

            void calcUnitVectors();
            veins::Coord normalizeVector(veins::Coord vector);
            veins::Coord crossProduct(veins::Coord vector1, veins::Coord vector2);
    };

} // end of namespace space_veins