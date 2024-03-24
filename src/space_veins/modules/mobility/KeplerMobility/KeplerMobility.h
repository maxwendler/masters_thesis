//
// Copyright (C) 2006-2012 Christoph Sommer <christoph.sommer@uibk.ac.at>
// Copyright (C) 2021 Mario Franke <research@m-franke.net>
// Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>
//
// Adaptation of SGP4Mobility class.
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

#include <fstream>

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