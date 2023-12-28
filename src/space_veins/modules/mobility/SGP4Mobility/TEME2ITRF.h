//
// Copyright (C) 2021 Mario Franke <research@m-franke.net>
//
// Documentation for these modules is at http://sat.car2x.org/
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

#include <cmath>
#include <utility>
#include <vector>
#include "space_veins/modules/mobility/SGP4Mobility/constants.h"

namespace space_veins {

/*
Helper function to use the same modulo operator as Python for floating point numbers.
*/
double pythonFmod(double, double);
std::pair<double, double> theta_GMST1982(double, double);
std::vector<double> multiply_outer(const std::vector<double> &, const double);

/* see skyfield/functions.py */
std::vector<std::vector<double>> rot_x(double);

/* see skyfield/functions.py */
std::vector<std::vector<double>> rot_y(double);

/* see skyfield/functions.py */
std::vector<std::vector<double>> rot_z(double);

/* computes the scalar/dot product of two vectors */
double dot(const std::vector<double> &, const std::vector<double> &);

/* 
 * computes a matrix multiplication a x b
 * Skyfield uses numpy.dot for matrix multiplication although ```matmul``` or ```@``` is preferred
 * see https://numpy.org/doc/stable/reference/generated/numpy.dot.html
 * see skyfield/sgp4lib.py
 */
std::vector<std::vector<double>> dot(const std::vector<std::vector<double>> &, const std::vector<std::vector<double>> &);

/* 
 * Matrix times vector: multiply a NxN matrix by a vector 
 * see https://numpy.org/doc/stable/reference/generated/numpy.einsum.html
 * einsum('ij...,j...->i...', M, v)
 * see skyfield/functions.py
 */
std::vector<double> mxv(const std::vector<std::vector<double>> &, const std::vector<double> &);

std::vector<double> v_plus_v(const std::vector<double> &, const std::vector<double> &);


/*
 * implements _cross(a, b) of skyfield/sgp4lib.py
 * I do not understand the python expression
 * my version computers the cross product
 */
std::vector<double> _cross(const std::vector<double> &, const std::vector<double> &);

std::pair<std::vector<double>, std::vector<double>> TEME_to_ITRF(double, std::vector<double>, std::vector<double>, double, double, double);

} // end namespace space_veins
