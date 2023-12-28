#pragma once
#include "veins/base/utils/Coord.h"
#include <tuple>
#include <fstream>
#include <random>
#include <math.h>
#include <vector>

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

            Cartesian2dInPlane cartesian2dSystem;
            
            CirclePlane():radius(0),angularVelocityPerSecRad(0){};
            CirclePlane(veins::Coord point1, veins::Coord point2, double radius, double angularVelocityPerSecRad);
            CirclePlane& operator=(const CirclePlane& other);

            veins::Coord getPointAtSecond(double t);

        protected:

            void calcUnitVectors();
            veins::Coord normalizeVector(veins::Coord vector);
            veins::Coord crossProduct(veins::Coord vector1, veins::Coord vector2);
    };

} // end of namespace space_veins