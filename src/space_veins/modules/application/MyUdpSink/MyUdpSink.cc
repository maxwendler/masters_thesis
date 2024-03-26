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

#include <string>

#include "space_veins/modules/application/MyUdpSink/MyUdpSink.h"

Define_Module(space_veins::MyUdpSink);

using namespace space_veins;

void MyUdpSink::initialize(int stage) {
    UdpSink::initialize(stage);
    if (stage == 0) {
        satelliteId = getParentModule()->getIndex();
    }
    if (stage == 1) {
        // initialize globalStatistics
        globalStatistics = GlobalStatisticsAccess().get(getParentModule()->getParentModule());
    }
}

void MyUdpSink::processPacket(inet::Packet *pk) {
    // register reception at globalStatistics module
    std::string pName(pk->getName());
    std::stringstream ss(pName);
    std::string s;
    std::vector<std::string> tokens;

    while(std::getline(ss, s, '-'))
    {
       tokens.push_back(s);
    }

    int pId = std::stoi(tokens[1]);

    EV_DEBUG << "register packet reception with Id: " << pId << std::endl;
    globalStatistics->registerReception(pId, satelliteId);
    UdpSink::processPacket(pk);
}

void MyUdpSink::finish() {
    UdpSink::finish();
}