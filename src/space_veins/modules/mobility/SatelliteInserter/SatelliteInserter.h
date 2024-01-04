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

#include <fstream>
#include <string>
#include "dirent.h"

#include "space_veins/space_veins.h"
#include "space_veins/modules/mobility/SGP4Mobility/TLE.h"

namespace space_veins {

class SPACE_VEINS_API SatelliteInserter : public cSimpleModule
{

    protected:
        virtual void initialize(int) override;

        int numInitStages() const override
        {
            return std::max(cSimpleModule::numInitStages(), 99);    // Satellite creation has to be done after everything from INET is initialized
        }

        virtual void finish() override;

        void parseTleFile(std::string path);
        void openTraceFiles(std::string dirPath);

        std::pair<std::string, unsigned int> getConstellationAndSatNum(TLE tle);
        std::pair<std::string, unsigned int> getConstellationAndSatNum(std::string tleName);

        void createSatellite(TLE tle, unsigned int satNum, unsigned int vectorSize, std::string constellation);
        void createSatellite(std::string traceFilePath, unsigned int satNum, unsigned int vectorSize, std::string constellation);

        void instantiateSatellite(TLE tle);
        void instantiateSatellite(std::string traceFilePath);

        unsigned int determineVectorSize(std::string constellation, unsigned int satNum);

    private:
        std::string mobilityType;
        std::string pathToTleFile;
        std::string pathToTracesDir;
        std::string satelliteModuleType;
        std::string satelliteModuleDefaultName;
        std::string satelliteConstellationsModuleName;
        std::string wall_clock_sim_start_time_utc;  // wall clock start time of the simulation's begin
        
        std::string avgSGP4AltitudesPath;
        bool useAvgSGP4Alts;
        std::map<std::string,double> avgSGP4Altitudes; 

        unsigned int satelliteVectorSize = 0;
        unsigned int starlinkVectorSize = 0;
        unsigned int iridiumVectorSize = 0;
        unsigned int onewebVectorSize = 0;
        unsigned int orbcommVectorSize = 0;
        unsigned int globalstarVectorSize = 0;
        unsigned int spacebeeVectorSize = 0;
        unsigned int spacebeenzVectorSize = 0;

        bool ignoreUnknownSatellites;
};
} // namespace space_veins
