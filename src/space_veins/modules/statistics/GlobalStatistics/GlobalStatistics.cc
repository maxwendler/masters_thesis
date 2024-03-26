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

#include "space_veins/modules/statistics/GlobalStatistics/GlobalStatistics.h"

#define PACKET_TIMER 0

Define_Module(space_veins::GlobalStatistics);

using namespace space_veins;

void GlobalStatistics::initialize(int stage)
{
    if (stage == 0) {
        EV_DEBUG << "GlobalStatistics initialized." << std::endl;

        packetTimer = new cMessage("packetTimer", PACKET_TIMER);
        packetTimerDelay = par("packetTimerDelay");
        WATCH(numTotalCars);
        WATCH(numRemovedCars);
        WATCH(numCurrentCars);
        WATCH(packetsReceived);
        WATCH(currentPacketId);
        WATCH(packetTimerDelay);

        vecCurrentCars.setName("vecCurrentCars:vector");
        vecPacketsReceived.setName("packetsReceived:vector");
        vecReceivingSatelliteIds.setName("receivingSatelliteIds:vector");
    }
}

void GlobalStatistics::finish() {
    recordScalar("numTotalCars", numTotalCars);
    recordScalar("numRemovedCars", numRemovedCars);
    recordScalar("numCurrentCars", numCurrentCars);
}

void GlobalStatistics::handleMessage(cMessage *msg)
{
    if (msg->isSelfMessage()) {
        handleSelfMessage(msg);
    }
}

void GlobalStatistics::handleSelfMessage(cMessage *msg) {
    if (msg->getKind() == PACKET_TIMER) {
        EV_DEBUG << "Written to vector, packetsReceived: " << packetsReceived << std::endl;
        vecPacketsReceived.record(packetsReceived);
        packetsReceived = 0;
        // store each id in receivingSatelliteIds in its vector
        for (auto id : receivingSatelliteIds)
        {
            vecReceivingSatelliteIds.record(id);
        }
        receivingSatelliteIds.clear();
    }
}

GlobalStatistics::~GlobalStatistics() {
}

void GlobalStatistics::incrementTotalCars()
{
    numTotalCars += 1;
    numCurrentCars += 1;
    vecCurrentCars.record(numCurrentCars);
}

void GlobalStatistics::incrementRemovedCars()
{
    numRemovedCars += 1;
    numCurrentCars -= 1;
    vecCurrentCars.record(numCurrentCars);
}

void GlobalStatistics::registerTransmission(int packetId) {
    currentPacketId = packetId;
    scheduleAt(simTime() + packetTimerDelay, packetTimer);
    EV_DEBUG << "registerTransmission - currentPacketId: " << currentPacketId << std::endl;
}

void GlobalStatistics::registerReception(int packetId, int satelliteId) {
    EV_DEBUG << "registerReception - packetId: " << packetId << ", currentPacketId: " << currentPacketId << std::endl;
    if (packetId == currentPacketId) {
        packetsReceived = packetsReceived + 1;
    }
    receivingSatelliteIds.insert(satelliteId);
}