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

        // Sets ifstream to read trace coordinates
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