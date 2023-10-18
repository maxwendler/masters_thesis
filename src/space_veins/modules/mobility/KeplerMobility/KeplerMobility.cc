#include "space_veins/modules/mobility/KeplerMobility/KeplerMobility.h"
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <proj.h>
#include <string>

using namespace space_veins;

Define_Module(space_veins::KeplerMobility);

// Not used atm to model SGP4 mobility, which also does not set initial position
void KeplerMobility::setInitialPosition()
{
    EV_DEBUG << "KeplerMobility setInitialPosition()" << std::endl;
    //AS WRITTEN IN SGP4Mobility: 
    //not possible at the moment because of dependencies in the initialize phase
    //updateSatellitePosition();
}

void KeplerMobility::initializePosition()
{
    EV_DEBUG << "SGP4Mobility initialPosition()" << std::endl;
    MovingMobilityBase::initializePosition();
}

void KeplerMobility::preInitialize(std::string traceFilePath)
{
    traceFile = std::ifstream(traceFilePath);
    // skip first line with satellite constellation and number
    traceFile.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    isPreInitialized = true;
}

void KeplerMobility::initialize(int stage)
{
    EV_DEBUG << "KeplerMobility stage: " << stage << std::endl;
    MovingMobilityBase::initialize(stage);
    
    if (stage == 0) {
        EV_DEBUG << "Initializing KeplerMobility module." << std::endl;
        EV_DEBUG << "isPreInitialized: " << isPreInitialized << std::endl;
        ASSERT(isPreInitialized);
        
        // create projection context
        pj_ctx = proj_context_create();

        // create wgs84_to_wgs84cartesian_projection
        wgs84_to_wgs84cartesian_projection = proj_create(
                pj_ctx,
                "+proj=pipeline +step proj=cart +ellps=WGS84");    // from WGS84 geodetic to cartesian
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
        EV_DEBUG << "KeplerMobility: ss_proj: " << ss_proj.str() << std::endl;
        // geocentric to topocentric projection
        wgs84cartesian_to_topocentric_projection = proj_create(pj_ctx, ss_proj.str().c_str());

        // Statistics
        vehicleStatistics = VehicleStatisticsAccess().get(getParentModule());
    }
}

void KeplerMobility::updateSatellitePosition()
{   
    // read next trace line
    std::string sat_pos_wgs84_str; 
    // ASSERT(traceFile->is_open());
    std::getline(traceFile, sat_pos_wgs84_str);
    char* sat_pos_wgs84_c_str = new char[sat_pos_wgs84_str.length() + 1];
    strcpy(sat_pos_wgs84_c_str, sat_pos_wgs84_str.c_str());
    
    // parse WGS84 coordinate from trace line
    std::string coord = std::strtok(sat_pos_wgs84_c_str, ",");        
    double wgs84lon = std::stod(coord, NULL);
    coord = std::strtok(NULL, ","); 
    double wgs84lat = std::stod(coord, NULL);
    coord = std::strtok(NULL, ",");
    double wgs84alt =  std::stod(coord, NULL);

    delete[] sat_pos_wgs84_c_str;

    // Transform satellite's WGS84 coordinate from geodetic to cartesian representation, proj needs Radians for an unknown reason
    // see https://proj.org/operations/conversions/cart.html
    PJ_COORD toTransfer = proj_coord(wgs84lon * (PI/180), wgs84lat * (PI/180), wgs84alt, 0);
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

void KeplerMobility::handleSelfMessage(cMessage* message)
{
    MovingMobilityBase::handleSelfMessage(message);
}

void KeplerMobility::move()
{
    updateSatellitePosition();
    //lastVelocity = inet::Coord();                       // TODO from SGP4Mobility: Consider the speed returned by the SGP4 model
    //lastOrientation = inet::Quaternion(0, 0, 0, 0);     // TODO from SGP4Mobility: Currently there are no values for the direction of the satellite

    EV_DEBUG << "MARIO: KeplerMobility move! SimTime: " << simTime() << std::endl;
    updateDisplayStringFromMobilityState();
}

void KeplerMobility::finish()
{
    MovingMobilityBase::finish();
    traceFile.close();
}