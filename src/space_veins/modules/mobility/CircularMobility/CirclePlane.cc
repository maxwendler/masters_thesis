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

#include "./CirclePlane.h"
#include <math.h>
#include <stdexcept>

using namespace space_veins;

CirclePlane::CirclePlane(veins::Coord point1, veins::Coord point2, double radius, double angularVelocityPerSecRad, double startRadOffset=0) :
    inPoint1(point1),
    inPoint2(point2),
    radius(radius),
    angularVelocityPerSecRad(angularVelocityPerSecRad),
    startRadOffset(startRadOffset)
{
    // ensure input vectors don't have same direction
    // factor for x2 * k = x1 would hold for y2 * k = y1
    double xFactor = inPoint1.x / inPoint2.x;
    double yFactor = inPoint1.y / inPoint2.y;
    double zFactor = inPoint1.z / inPoint2.z;

    if (xFactor == yFactor && xFactor == zFactor){
        throw std::invalid_argument("The two input vectors for creating the circle plane are parallel and hence cannot be used to define a circle plane!");
    }

    calcUnitVectors();
}

CirclePlane& CirclePlane::operator=(const CirclePlane& other)
{
    if (this != &other)
    {
        cartesian2dSystem = other.cartesian2dSystem;

        const_cast<double&>(radius) = other.radius;
        const_cast<double&>(startRadOffset) = other.startRadOffset;
        const_cast<veins::Coord&>(inPoint1) = other.inPoint1;
        const_cast<veins::Coord&>(inPoint2) = other.inPoint2;
        const_cast<double&>(angularVelocityPerSecRad) = other.angularVelocityPerSecRad;
    }
    return *this;
}

void CirclePlane::calcUnitVectors()
{
    cartesian2dSystem.unitXVector = normalizeVector(inPoint1);
    
    // Calculate perpendicular vector two both input vectors to then calculate perpendicular vector 
    // to this new vector and the unitXVector, yielding a perpendicular vector in the CirclePlane, i.e. the unitYVector.
    veins::Coord normalVec = crossProduct(cartesian2dSystem.unitXVector, inPoint2);
    veins::Coord yVector = crossProduct(normalVec, cartesian2dSystem.unitXVector);
    cartesian2dSystem.unitYVector = normalizeVector(yVector); 
}

// 0 radians at inPoint1
veins::Coord CirclePlane::getPointAtSecond(double t)
{   
    double radians = fmod( angularVelocityPerSecRad * t + startRadOffset, 2 * M_PI);

    double x_in_2d = radius * cos(radians);
    double y_in_2d = radius * sin(radians);

    double x = cartesian2dSystem.unitXVector.x * x_in_2d + cartesian2dSystem.unitYVector.x * y_in_2d;
    double y = cartesian2dSystem.unitXVector.y * x_in_2d + cartesian2dSystem.unitYVector.y * y_in_2d;
    double z = cartesian2dSystem.unitXVector.z * x_in_2d + cartesian2dSystem.unitYVector.z * y_in_2d;

    return veins::Coord(x, y, z);   
}

veins::Coord CirclePlane::normalizeVector(veins::Coord vector)
{   
    double x = vector.x;
    double y = vector.y;
    double z = vector.z;
    double vectorLength = sqrt(pow(x,2) + pow(y,2) + pow(z,2));
    return veins::Coord(x / vectorLength, y / vectorLength, z / vectorLength);
}

veins::Coord CirclePlane::crossProduct(veins::Coord vector1, veins::Coord vector2)
{
    double crossX = vector1.y * vector2.z - vector1.z * vector2.y;
    double crossY = vector1.z * vector2.x - vector1.x * vector2.z;
    double crossZ = vector1.x * vector2.y - vector1.y * vector2.x;
    return veins::Coord(crossX, crossY, crossZ);
}