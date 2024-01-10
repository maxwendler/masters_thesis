#pragma once

#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <chrono>

#include <proj.h>
#include <vector>

#include "inet/mobility/base/MovingMobilityBase.h"
#include "inet/common/geometry/common/Coord.h"

#include "space_veins/space_veins.h"
#include "space_veins/modules/utility/WGS84Coord.h"
#include "space_veins/modules/mobility/SGP4Mobility/TLE.h"
#include "space_veins/modules/mobility/SGP4Mobility/SGP4.h"
#include "space_veins/modules/SatelliteObservationPoint/SatelliteObservationPoint.h"
#include "space_veins/modules/statistics/VehicleStatistics/VehicleStatistics.h"

#include "space_veins/modules/mobility//CircularMobility/CirclePlane.h"

#include "veins/modules/mobility/traci/TraCIScenarioManager.h"
#include "veins/modules/mobility/traci/TraCIConnection.h"
#include "veins/base/utils/FindModule.h"
#include "veins/base/utils/Heading.h"
#include "veins/base/utils/Coord.h"
#include "veins/base/utils/FWMath.h"

namespace space_veins {

class SPACE_VEINS_API CircularMobility : public inet::MovingMobilityBase {

     struct date_time_t {
            int year;
            int mon;
            int day;
            int hour;
            int min;
            double sec;
        };

    protected:
       
        int circlePlane2ndPointHalfOrbitTenth; 
        double avgSGP4Altitude;
        std::string circlePlanePointsSource;

        bool isPreInitialized;

        // Proj projections
        PJ_CONTEXT* pj_ctx;
        PJ* itrf2008_to_wgs84_projection;
        PJ* wgs84_to_wgs84cartesian_projection;
        PJ* wgs84cartesian_to_topocentric_projection;

        // SOP pointer
        SatelliteObservationPoint* sop;

        /* Statistics */
        VehicleStatistics* vehicleStatistics;
        
        // SGP4
        elsetrec satrec;

        // TLE data
        TLE tle;

        // Time management
        // wall clock start time utc
        std::string wall_clock_sim_start_time_utc;  // wall clock start time of the simulation's begin
        date_time_t wall_clock_start_time;          // wall clock start time of the simulation's begin as date_time_t object
        double wall_clock_sim_start_time_jd;        // julian date of the simulation's begin
        double wall_clock_sim_start_time_frac;      // fraction of the day of the simulation's begin for julian date
        // TLE epoch
        date_time_t tle_epoch;                      // date_time_t of the TLE's epoch
        double tle_epoch_jd;                        // julian date of the TLE's epoch
        double tle_epoch_frac;                      // fraction of the day of the TLE's epoch for julian date
        // Current wall clock time as julian data
        double current_wall_clock_time_jd;          // current wall clock time as julian date
        double current_wall_clock_time_frac;        // fraction of the day of the current wall clock time for julian date
        // Difference Tle epoch current wall clock time in minutes
        double diffTleEpochWctMin;                  // difference between the TLE's epoch and the wall clock start time in minutes

        std::pair<std::vector<double>, std::vector<double>> calcSatellitePositionTEME(double simTimeMinutes);

        // Circle plane
        CirclePlane circlePlane;

    public:
        CircularMobility()
            : MovingMobilityBase(),
            isPreInitialized(false) 
        {           
        }
        ~CircularMobility() override
        {
        }

        // Sets ifstream to read trace coordinates.
        void preInitialize(TLE pTle, std::string pWall_clock_sim_start_time_utc, double avgSGP4Altitude);
        
        // from SGP4Mobility
        void updateSatellitePosition();

        // from cSimpleModule
        void finish() override;

        // from MobilityBase
        void setInitialPosition() override;
        int numInitStages() const override
        {
            return std::max(cSimpleModule::numInitStages(), 5);
        }

        void set_TLE(const TLE tle);

        TLE get_TLE() const;
        
        // from MovingMobilityBase
        void initialize(int) override;
        void initializePosition() override;
        virtual void handleSelfMessage(cMessage* message) override;
        virtual void move() override;
        virtual inet::Coord getCurrentPosition() override { return lastPosition; }
        virtual inet::Coord getCurrentVelocity() override { return inet::Coord::ZERO; }
        virtual inet::Quaternion getCurrentAngularPosition() override { return inet::Quaternion::IDENTITY; }
        virtual inet::Coord getCurrentAcceleration() override { return inet::Coord::ZERO; }
    
    class SPACE_VEINS_API CircularMobilityAccess {
        public:
            CircularMobility* get(cModule* host)
            {
                CircularMobility* circular = veins::FindModule<CircularMobility*>::findSubModule(host);
                ASSERT(circular);
                return circular;
            };
    };
};

}