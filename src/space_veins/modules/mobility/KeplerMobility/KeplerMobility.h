#pragma once

#include <fstream>
#include <iostream>

#include <proj.h>

#include "inet/mobility/base/MovingMobilityBase.h"

#include "space_veins/space_veins.h"
#include "space_veins/modules/SatelliteObservationPoint/SatelliteObservationPoint.h"
#include "space_veins/modules/statistics/VehicleStatistics/VehicleStatistics.h"

namespace space_veins {

class SPACE_VEINS_API KeplerMobility : public inet::MovingMobilityBase {

    protected:
        // only MIGHT be necessary
        bool isPreInitialized;
        // proj context
        PJ_CONTEXT* pj_ctx;
        // one or multiple projections for wgs84 to topodetic
        PJ* wgs84_to_wgs84cartesian_projection;
        PJ* wgs84cartesian_to_topocentric_projection;

        // SOP pointer
        SatelliteObservationPoint* sop;

        /* Time management - REQUIRED???
        date_time_t tle_epoch;                      // date_time_t of the TLE's epoch
        std::chrono::system_clock::time_point ep;
        std::string wall_clock_sim_start_time_utc;  // wall clock start time of the simulation's begin
        date_time_t wall_clock_start_time;          // wall clock start time of the simulation's begin as date_time_t object
        std::chrono::system_clock::time_point wct;  // current wall clock time
        std::chrono::duration<double, std::chrono::minutes::period> wall_clock_since_tle_epoch_min;  // elapsed minutes since tle epoch considering configured wall clock start time in UTC and elapsed simulation time
        date_time_t current_date_time;
        */

        /* Statistics */
        VehicleStatistics* vehicleStatistics;

        // file stream from which coordinates will be continiously read
        std::ifstream* traceFilePtr;
        std::ifstream traceFile;

    public:
        KeplerMobility()
            : MovingMobilityBase(),
            isPreInitialized(false) 
        {           
        }
        ~KeplerMobility() override
        {
        }

        // Sets ifstream to read trace coordinates.
        void preInitialize(std::ifstream* pTraceFile);
        void preInitialize(std::string traceFilePath);
        
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

        // from MovingMobilityBase
        void initialize(int) override;
        void initializePosition() override;
        virtual void handleSelfMessage(cMessage* message) override;
        virtual void move() override;
        virtual inet::Coord getCurrentPosition() override { return lastPosition; }
        virtual inet::Coord getCurrentVelocity() override { return inet::Coord::ZERO; }
        virtual inet::Quaternion getCurrentAngularPosition() override { return inet::Quaternion::IDENTITY; }
        virtual inet::Coord getCurrentAcceleration() override { return inet::Coord::ZERO; }
    
    class SPACE_VEINS_API KeplerMobilityAccess {
        public:
            KeplerMobility* get(cModule* host)
            {
                KeplerMobility* kepler = veins::FindModule<KeplerMobility*>::findSubModule(host);
                ASSERT(kepler);
                return kepler;
            };
    };
};

}