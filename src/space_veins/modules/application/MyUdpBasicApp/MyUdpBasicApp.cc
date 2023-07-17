//
// Copyright (C) 2023 Mario Franke <research@m-franke.net>
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

#include "space_veins/modules/application/MyUdpBasicApp/MyUdpBasicApp.h"

#include "inet/mobility/contract/IMobility.h"

Define_Module(space_veins::MyUdpBasicApp);

using namespace space_veins;

void MyUdpBasicApp::initialize(int stage) {
    UdpBasicApp::initialize(stage);

    if (stage == 4) {
        // initialize globalStatistics
        globalStatistics = GlobalStatisticsAccess().get(getParentModule()->getParentModule());
        vehicleStatistics = VehicleStatisticsAccess().get(getParentModule());
        sop = SatelliteObservationPointAccess().get();
        ASSERT(sop);
    }
}

void MyUdpBasicApp::sendPacket()
{
    UdpBasicApp::sendPacket();
    // register packet at globalStatistics module
    // has to be numSent - 1, because UdpBasicApp increases numSent after sending a packet.
    EV_DEBUG << "register packet transmission with Id: " << numSent - 1 << std::endl;
    globalStatistics->registerTransmission(numSent - 1);
}

void MyUdpBasicApp::finish() {
    UdpBasicApp::finish();
    cModule* host = getContainingNode(this);
    inet::IMobility* mobility = check_and_cast<inet::IMobility *>(host->getSubmodule("mobility"));
    auto pos = mobility->getCurrentPosition();
    veins::Coord veins_pos(pos.x, pos.y, pos.z);
    auto wgs84coord = sop->omnet2WGS84(veins_pos);
    vehicleStatistics->recordOmnetCoord(veins_pos);
    vehicleStatistics->recordWGS84Coord(wgs84coord);
}