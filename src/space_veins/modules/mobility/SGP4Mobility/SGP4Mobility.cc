//
// Copyright (C) 2006-2012 Christoph Sommer <christoph.sommer@uibk.ac.at>
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

#include "space_veins/modules/mobility/SGP4Mobility/SGP4Mobility.h"
#include "space_veins/modules/mobility/SGP4Mobility/TEME2ITRF.h"
#include "veins/base/utils/Coord.h"

using namespace space_veins;

Define_Module(space_veins::SGP4Mobility);

void SGP4Mobility::setInitialPosition()
{
    EV_DEBUG << "SGP4Mobility setInitialPosition()" << std::endl;
    // not possible at the moment because of dependencies in the initialize phase
    //updateSatellitePosition();
}

void SGP4Mobility::initializePosition()
{
    EV_DEBUG << "SGP4Mobility initialPosition()" << std::endl;
    MovingMobilityBase::initializePosition();
}

void SGP4Mobility::preInitialize(TLE pTle, std::string pWall_clock_sim_start_time_utc)
{
    EV_DEBUG << "SGP4Mobility preInitialize()" << std::endl;
    tle = pTle;
    wall_clock_sim_start_time_utc = pWall_clock_sim_start_time_utc;
    isPreInitialized = true;
}

void SGP4Mobility::initialize(int stage)
{
    EV_DEBUG << "SGP4Mobility stage: " << stage << std::endl;
    MovingMobilityBase::initialize(stage);
    if (stage == 0) {

        EV_DEBUG << "Initializing SGP4Mobility module." << std::endl;
        EV_DEBUG << "isPreInitialized: " << isPreInitialized << std::endl;
        ASSERT(isPreInitialized);
        WATCH(tle.satellite_name);
        WATCH(tle.tle_line1);
        WATCH(tle.tle_line2);
        WATCH(wall_clock_sim_start_time_utc);
        EV_DEBUG << "SGP4 model wall_clock_sim_start_time_utc: " << wall_clock_sim_start_time_utc << std::endl;
        std::istringstream iss(wall_clock_sim_start_time_utc);
        std::tm tmp;    // helper struct to read in the wall_clock_sim_start_time_utc
        iss >> std::get_time(&tmp, "%Y-%m-%d-%H-%M-%S");

        wall_clock_start_time.year = tmp.tm_year + 1900;  //tm_year is number of year after 1900 according to struct
        wall_clock_start_time.mon = tmp.tm_mon + 1;       //tm_mon is number of months after Jan (Jan = 0)
        wall_clock_start_time.day = tmp.tm_mday;
        wall_clock_start_time.hour = tmp.tm_hour;
        wall_clock_start_time.min = tmp.tm_min;
        wall_clock_start_time.sec = tmp.tm_sec;

        EV_DEBUG << "SGP4 model time initialized to: year: " << wall_clock_start_time.year
                 << " month: " << wall_clock_start_time.mon
                 << " day: " << wall_clock_start_time.day
                 << " hour: " << wall_clock_start_time.hour
                 << " minute: " << wall_clock_start_time.min
                 << " second: " << wall_clock_start_time.sec
                 << std::endl;

        // Store current wall clock time (wct) as std::chrono::system_clock::time_point
        setenv("TZ", "/usr/share/zoneinfo/posix/UTC", 1); // POSIX-specific
        std::tm tm = {};
        std::stringstream ss(wall_clock_sim_start_time_utc);
        ss >> std::get_time(&tm, "%Y-%m-%d-%H-%M-%S");
        wct = std::chrono::system_clock::from_time_t(std::mktime(&tm));

        // create projection context
        pj_ctx = proj_context_create();

        // create itrf2008_to_wgs84_projection
        itrf2008_to_wgs84_projection = proj_create_crs_to_crs(
                pj_ctx,
                "EPSG:5332",    // from ITRF2008
                "EPSG:4326",    // to WGS84
                NULL);

        // fix longitude, latitude order, see https://proj.org/development/quickstart.html
        itrf2008_to_wgs84_projection = proj_normalize_for_visualization(pj_ctx, itrf2008_to_wgs84_projection);
        if (itrf2008_to_wgs84_projection == 0) {
            throw cRuntimeError("itrf2008_to_wgs84_projection initialization error");
        }

        // create wgs84_to_wgs84cartesian_projection
        wgs84_to_wgs84cartesian_projection = proj_create(
                pj_ctx,
                "+proj=pipeline +step proj=cart +ellps=WGS84");    // from WGS84 geodetic to cartesian

        // Initialize SGP4 model
        double startmfe = -2880;  // in min -> 2 days before epoch
        double stopmfe = 2880;  // in min -> 2 days after epoch
        double deltamin = 1/600; // in min -> 1/60 is 1 second -> 1/600 is 0.1 second
        SGP4Funcs::twoline2rv((char*)tle.get_tle_line1().c_str(),
                              (char*)tle.get_tle_line2().c_str(),
                              'c', // catalog run
                              'd', // type of manual input, d = dayofyr, possible irrelevant because no manual run is performed
                              'i', //improved mode
                              gravconsttype::wgs72,     // used by Skyfield
                              startmfe,
                              stopmfe,
                              deltamin,
                              satrec);

        // Store tle epoch as date_time_t object
        tle_epoch.year = (satrec.epochyr >= 57) ? 1900 + satrec.epochyr : 2000 + satrec.epochyr;
        SGP4Funcs::days2mdhms_SGP4(satrec.epochyr,
                                   satrec.epochdays,
                                   tle_epoch.mon,
                                   tle_epoch.day,
                                   tle_epoch.hour,
                                   tle_epoch.min,
                                   tle_epoch.sec
                                   );

        // Calculate elapsed time beginning from the tle epoch
        std::stringstream ss2;
        std::tm tm_tle_epoch = {};
        ss2 << tle_epoch.year << "-" << std::setfill('0') << std::setw(2) << tle_epoch.mon << "-" << tle_epoch.day << "-" << tle_epoch.hour << "-" << tle_epoch.min << "-" << tle_epoch.sec;
        EV_DEBUG << "tle_epoch: " << ss2.str() << std::endl;
        ss2 >> std::get_time(&tm_tle_epoch, "%Y-%m-%d-%H-%M-%S");
        ep = std::chrono::system_clock::from_time_t(std::mktime(&tm_tle_epoch)); // tle epoch

        std::time_t toPrint = std::chrono::system_clock::to_time_t(wct);
        EV_DEBUG << "Current wall clock time: wct: " << std::put_time(std::gmtime(&toPrint), "%c %Z") << std::endl;

        toPrint = std::chrono::system_clock::to_time_t(ep);
        EV_DEBUG << "TLE epoch: ep: " << std::put_time(std::gmtime(&toPrint), "%c %Z") << std::endl;

        wall_clock_since_tle_epoch_min = std::chrono::duration<double, std::chrono::minutes::period>(wct - ep);
        EV_DEBUG << "wall_clock_since_tle_epoch_min: wct - ep: " << wall_clock_since_tle_epoch_min.count() << " min" << std::endl;
    }
    if (stage == 4) {
        // has to be done after the SOP stage in which the sop_omnet_coord is retrieved from its mobility
        // Get access to SOP
        sop = SatelliteObservationPointAccess().get();
        ASSERT(sop);
        const PJ_COORD sop_wgs84_proj_cart = sop->get_sop_wgs84_proj_cart();
        // create geocentric to topocentric projection (requires sop_wgs84 as Cartesian coordinate)
        std::stringstream ss_proj;
        ss_proj << "+proj=topocentric +ellps=WGS84 +X_0=" << sop_wgs84_proj_cart.xyz.x << " +Y_0=" << sop_wgs84_proj_cart.xyz.y << " +Z_0=" << sop_wgs84_proj_cart.xyz.z;
        EV_DEBUG << "SGP4Mobility: ss_proj: " << ss_proj.str() << std::endl;
        // geocentric to topocentric projection
        wgs84cartesian_to_topocentric_projection = proj_create(pj_ctx, ss_proj.str().c_str());

        // Statistics
        vehicleStatistics = VehicleStatisticsAccess().get(getParentModule());
    }
}

void SGP4Mobility::updateSatellitePosition()
{
    // t is the duration from tle epoch until current simTime() in minutes as required by SGP4Funcs::sgp4
    std::chrono::duration<double, std::chrono::minutes::period> t = wall_clock_since_tle_epoch_min + std::chrono::duration<double, std::chrono::milliseconds::period>(simTime().dbl() * 1000);
    EV_DEBUG << "SGP4Mobility wall_clock_since_tle_epoch_min: " << wall_clock_since_tle_epoch_min.count() << " min" << std::endl;
    EV_DEBUG << "SGP4Mobility wall_clock_since_tle_epoch_min + simTime(): " << t.count() << " min" << std::endl;

    // Calculate satellite position using SGP4 in TEME coodinate system
    double r_array[3];
    double v_array[3];
    bool ret = SGP4Funcs::sgp4(satrec,
                            (double)t.count(),          // time since epoch in min
                            r_array,
                            v_array);
    // Copy results into a vector
    int n = sizeof(r_array) / sizeof(r_array[0]);
    std::vector<double> r_TEME(r_array, r_array + n);
    std::vector<double> v_TEME(v_array, v_array + n);

    // Calculate the current date_time_t which is required in order to calculate the date according to the Julian calendar
    // SGP4 Model needs the current SGP4Mobility::date_time_t: tle_epoch + t as date -> DD-MM-YYYY:HH-mm-SS.SSS
    // Transform duration t from minutes in needed period
    std::chrono::duration<double, std::chrono::milliseconds::period> tp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t);

    auto cdtTimeT = std::chrono::system_clock::to_time_t(ep) + ((long)(tp_ms.count()) / 1000);
    EV_TRACE << "tp_s count: " << (long)(tp_ms.count()) / (double)1000 << std::endl;
    EV_TRACE << "system_clock is steady: " << std::chrono::system_clock::is_steady << std::endl;
    std::tm cdt = *(std::gmtime(&cdtTimeT));
    cdt.tm_year += 1900;
    cdt.tm_mon += 1;

    EV_TRACE << "SGP4Mobility cdt: year: " << cdt.tm_year
             << ",  month: " << cdt.tm_mon
             << ",  day: " << cdt.tm_mday
             << ",  hour: " << cdt.tm_hour
             << ",  minute: " << cdt.tm_min
             << ",  second: " << cdt.tm_sec + ((double)((int)tp_ms.count() % 1000) / 1000)
             << std::endl;

    // Calculate julian date_time for TEME to ITRF conversion
    double julian_day, julian_day_frac;
    SGP4Funcs::jday_SGP4(cdt.tm_year,
                         cdt.tm_mon,
                         cdt.tm_mday,
                         cdt.tm_hour,
                         cdt.tm_min,
                         (double)(cdt.tm_sec) + ((double)((int)tp_ms.count() % 1000) / 1000),
                         julian_day,
                         julian_day_frac);

    julian_day += julian_day_frac;
    // Coordinate transformation TEME -> ITRF
    std::pair<std::vector<double>, std::vector<double>> itrf = TEME_to_ITRF(julian_day, r_TEME, v_TEME);
    vehicleStatistics->recordItrfCoord(veins::Coord(itrf.first[0], itrf.first[1], itrf.first[2]));
    // Coordinate transformation ITRF -> WGS84
    PJ_COORD toTransfer = proj_coord(itrf.first[0] * 1000, itrf.first[1] * 1000, itrf.first[2] * 1000, 0); // conversion km -> m!
    PJ_COORD geo = proj_trans(itrf2008_to_wgs84_projection, PJ_FWD, toTransfer);
    WGS84Coord sat_pos_wgs84 = WGS84Coord(geo.lpz.phi, geo.lpz.lam, geo.lpz.z);
    vehicleStatistics->recordWGS84Coord(sat_pos_wgs84);
    EV_TRACE << "SGP4Mobility simTime(): " << simTime() << std::endl;
    EV_TRACE << "SGP4Mobility sat_pos_wgs84: " << sat_pos_wgs84 << std::endl;

    // Transform satellite's WGS84 coordinate from geodetic to cartesian representation, proj needs Radians for an unknown reason
    // see https://proj.org/operations/conversions/cart.html
    toTransfer = proj_coord(sat_pos_wgs84.lon * (PI/180), sat_pos_wgs84.lat * (PI/180), sat_pos_wgs84.alt, 0);
    PJ_COORD geo_cart = proj_trans(wgs84_to_wgs84cartesian_projection, PJ_FWD, toTransfer);
    vehicleStatistics->recordWGS84CartCoord(geo_cart);
    EV_TRACE << "SGP4Mobility sat_pos_wgs84 cartesian: x: " << geo_cart.xyz.x << ", y: " << geo_cart.xyz.y << ", z: " << geo_cart.xyz.z << std::endl;

    // Geocentric to topocentric, see https://proj.org/operations/conversions/topocentric.html
    PJ_COORD topo_cart = proj_trans(wgs84cartesian_to_topocentric_projection, PJ_FWD, geo_cart);
    EV_TRACE << "SGP4Mobility topo as cartesian coordinates: e: " << topo_cart.enu.e << ", n:" << -topo_cart.enu.n << ", u: " << topo_cart.enu.u << std::endl;
    vehicleStatistics->recordSopRelativeCoord(veins::Coord(topo_cart.enu.e, -topo_cart.enu.n, topo_cart.enu.u));

    // Note the minus operator at the northing: The reason is OMNeT++'s coordinate system. The origin is in the upper left corner,
    // the x-axis goes from west to east in the positiv direction and the y-axis goes from north to south in the positiv direction.
    // According to the figure at https://proj.org/operations/conversions/topocentric.html the enu.n-axis needs to be inverted.
    //
    // Further, the position of the SOP is added such that the satellite position is relative to OMNeT++'s origin.
    auto sop_omnet_coord = sop->get_sop_omnet_coord();
    inet::Coord satellitePosition(topo_cart.enu.e + sop_omnet_coord.x, -topo_cart.enu.n + sop_omnet_coord.y, topo_cart.enu.u + sop_omnet_coord.z);
    EV_TRACE << "SGP4Mobility new lastPosition: " << satellitePosition << std::endl;

    lastPosition = satellitePosition;
    vehicleStatistics->recordOmnetCoord(veins::Coord(lastPosition.x, lastPosition.y, lastPosition.z));
}

void SGP4Mobility::handleSelfMessage(cMessage* message)
{
    MovingMobilityBase::handleSelfMessage(message);
}

void SGP4Mobility::move()
{
    updateSatellitePosition();
    lastVelocity = inet::Coord();                       // TODO: Consider the speed returned by the SGP4 model
    //lastOrientation = inet::Quaternion(0, 0, 0, 0);     // TODO: Currently there are no values for the direction of the satellite

    EV_DEBUG << "MARIO: SGP4Mobility move! SimTime: " << simTime() << std::endl;
    updateDisplayStringFromMobilityState();
}

void SGP4Mobility::finish()
{
    MovingMobilityBase::finish();
}
