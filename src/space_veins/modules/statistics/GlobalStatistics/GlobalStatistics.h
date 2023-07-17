//
// Copyright (C) 2021 Mario Franke <research@m-franke.net>
//
// SPDX-License-Identifier: GPL-2.0-or-later
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

#pragma once

#include <set>

#include "veins/veins.h"

#include "veins/base/utils/FindModule.h"
#include "veins/base/utils/Coord.h"

#include "space_veins/space_veins.h"
#include "space_veins/modules/utility/WGS84Coord.h"

using namespace omnetpp;

namespace space_veins {
class SPACE_VEINS_API GlobalStatistics : public cSimpleModule
{
    protected:
        virtual void initialize(int stage) override;
        virtual void finish() override;
        virtual void handleMessage(cMessage *msg) override;
        virtual void handleSelfMessage(cMessage *msg);
        ~GlobalStatistics();

    protected:
        unsigned long numTotalCars = 0;
        unsigned long numRemovedCars = 0;
        unsigned long numCurrentCars = 0;

        unsigned long packetsReceived = 0;
        cMessage* packetTimer;
        double packetTimerDelay;
        int currentPacketId = 0;
        std::set<int> receivingSatelliteIds;

        cOutVector vecCurrentCars;
        cOutVector vecPacketsReceived;
        cOutVector vecReceivingSatelliteIds;

    public:
        void incrementTotalCars();
        void incrementRemovedCars();

        void registerTransmission(int packetId);
        void registerReception(int packetId, int satelliteId);
};
}

namespace space_veins {
class SPACE_VEINS_API GlobalStatisticsAccess {
public:
    GlobalStatistics* get(cModule* host)
    {
        GlobalStatistics* vs = veins::FindModule<GlobalStatistics*>::findSubModule(host);
        ASSERT(vs);
        return vs;
    };
};
}
