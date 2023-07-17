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

#include "inet/applications/udpapp/UdpBasicApp.h"
#include "inet/mobility/static/StationaryMobility.h"

#include "space_veins/modules/statistics/GlobalStatistics/GlobalStatistics.h"
#include "space_veins/modules/statistics/VehicleStatistics/VehicleStatistics.h"
#include "space_veins/modules/SatelliteObservationPoint/SatelliteObservationPoint.h"

namespace space_veins {

class SPACE_VEINS_API MyUdpBasicApp : public inet::UdpBasicApp {

public:
    MyUdpBasicApp()
        : UdpBasicApp()
    {
    }

    ~MyUdpBasicApp()
    {
    }

protected:
    GlobalStatistics* globalStatistics;

    VehicleStatistics* vehicleStatistics;

    // SOP pointer
    SatelliteObservationPoint* sop;

protected:
    virtual void sendPacket() override;
    virtual void initialize(int stage) override;
    virtual void finish() override;
    virtual int numInitStages() const override { return inet::NUM_INIT_STAGES; }

};
} // namespace space_veins