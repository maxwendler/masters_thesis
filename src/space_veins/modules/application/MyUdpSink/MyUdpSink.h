//
// Copyright (C) 2023 Mario Franke <research@m-franke.net>
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

#pragma once

#include "inet/applications/udpapp/UdpSink.h"

#include "space_veins/modules/statistics/GlobalStatistics/GlobalStatistics.h"

namespace space_veins {

class SPACE_VEINS_API MyUdpSink : public inet::UdpSink {

public:
    MyUdpSink()
        : UdpSink()
    {
    }

    ~MyUdpSink() 
    {
    }

protected:
    GlobalStatistics* globalStatistics;
    int satelliteId = 0;

protected:
    virtual void processPacket(inet::Packet *msg) override;
    virtual void initialize(int stage) override;
    virtual void finish() override;
};
} // namespace space_veins