//
// Copyright (C) 2006-2017 Christoph Sommer <sommer@ccs-labs.org>
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

#include <algorithm>
#include <cctype>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <regex>
#include <string>
#include <utility>
#include <vector>
#include <boost/algorithm/string/trim.hpp>

#include "space_veins/modules/mobility/KeplerMobility/KeplerMobility.h"
#include "space_veins/modules/mobility/SatelliteInserter/SatelliteInserter.h"
#include "space_veins/modules/mobility/SGP4Mobility/SGP4Mobility.h"

using namespace space_veins;

Define_Module(space_veins::SatelliteInserter);


void SatelliteInserter::initialize(int stage)
{
    switch (stage)
    {
        case 0:
            mobilityType = par("mobilityType").stringValue();
            ASSERT(mobilityType != "None");
            if (mobilityType == "SGP4") pathToTleFile = par("pathToTleFile").stringValue();
            if (mobilityType == "Kepler") pathToTracesDir = par("pathToTracesDir").stringValue();

            satelliteModuleType = par("satelliteModuleType").stringValue();
            satelliteModuleDefaultName = par("satelliteModuleDefaultName").stringValue();
            wall_clock_sim_start_time_utc = par("wall_clock_sim_start_time_utc").stringValue();
            ignoreUnknownSatellites = par("ignoreUnknownSatellites").boolValue();
            break;

        case 98:
            if (mobilityType == "SGP4") parseTleFile(pathToTleFile);
            if (mobilityType == "Kepler")
            {           
                openTraceFiles(pathToTracesDir);
            } 
            break;
    }
}

void SatelliteInserter::parseTleFile(std::string path)
{
    std::ifstream tleFile(path);
    std::string tleLine;
    int tleLineNumber = 0;
    TLE tle;
    while (std::getline(tleFile, tleLine))
    {
        switch (tleLineNumber)
        {
            case 0:
                tle.set_satellite_name(tleLine);
                break;
            case 1:
                tle.set_tle_line1(tleLine);
                break;
            case 2:
                tle.set_tle_line2(tleLine);
                EV_DEBUG << "Initializing satellite: " << std::endl << tle << std::endl;
                instantiateSatellite(tle);
                break;
        }
        if (tleLineNumber < 2) {
            tleLineNumber++;
        }else{
            tleLineNumber = 0;
        }
    }
    // Check completeness of all satellites
    if (tleLineNumber != 0) {
        throw cRuntimeError("Incomplete satellite TLE");
    }
}

void SatelliteInserter::openTraceFiles(std::string path)
{
    DIR *dir;
    struct dirent *ent;
    dir = opendir(path.c_str());
    ASSERT(dir != nullptr);

    // instantiate satellites with opened ifstreams for all .trace files in dir
    while ((ent = readdir (dir)) != NULL) {
        std::string fname = ent->d_name;
        if (fname.find(".trace") != std::string::npos){
            EV_DEBUG << "Initializing satellite: " << std::endl << ent->d_name << std::endl;
            instantiateSatellite(std::string(path) + ent->d_name);
        }
    }
    
    closedir(dir);
}

std::pair<std::string, unsigned int> SatelliteInserter::getConstellationAndSatNum(TLE tle)
{
    std::string satelliteName = tle.get_satellite_name();
    std::vector<std::string> delimiters = {"-", " "};
    size_t posConstellation = std::string::npos;
    std::string delimiter;
    for (auto iter = delimiters.begin(); iter != delimiters.end(); ++iter) {
        posConstellation = satelliteName.find(*iter);
        if(satelliteName[posConstellation - 1] == '[' && satelliteName[posConstellation + 1] == ']') {
            // Some satellite names have a suffix "[-]". This occurence of "-" should not be treated as a delimiter.
            posConstellation = std::string::npos;
            continue;
        }
        if (posConstellation != std::string::npos) {
            // we found the correct delimiter, we can stop searching
            delimiter = *iter;
            break;
        }
    }
    std::string constellation = satelliteName.substr(0, posConstellation);
    satelliteName.erase(0, posConstellation + delimiter.length());
    // Delete non-numeric characters
    std::string regex = R"([\D])";
    satelliteName = std::regex_replace(satelliteName, std::regex(regex), "");
    // Delete leading zeros
    satelliteName.erase(0, satelliteName.find_first_not_of('0'));
    unsigned int satNum;
    try {
        satNum = std::stoul(satelliteName, nullptr, 0);
    }
    catch (const std::invalid_argument& ia) {
        // if satNum is not a number, use the catalog number 
        satNum = std::stoul(tle.get_tle_line1().substr(2, 5));
    }
    if (satNum == 0) {
        EV_DEBUG << "stop" << std::endl;
    }
    return std::pair<std::string, unsigned int>(constellation, satNum);
}

std::pair<std::string, unsigned int> SatelliteInserter::getConstellationAndSatNum(std::string tleName)
{   
    // 'STARLINK-1045' or 'STARLINK-1045 *' 
    std::regex format1(R"(\w+-\d+(?:\s.*)*)");
    // 'STARLINK 1045' or 'STARLINK 1045 *'
    std::regex format2(R"(\w+\s\d+(?:\s.*)*)");
    // one or more (word + whitespaces), i.e. no number
    std::regex format3(R"(\w+([\s,-].*\D+.*)*)");

    boost::algorithm::trim(tleName);

    // replace special characters "." and "/"
    for (int i=0; i < tleName.size(); i++){
        if (tleName[i] == '.' || tleName[i] == '/'){
            tleName.replace(i, 1, "-");
        }
    }

    std::string satName = "";
    unsigned int satNum = 0;

    if (std::regex_match(tleName, format1))
    {
        int delimiterPos1 = tleName.find("-");
        int delimiterPos2 = tleName.find(" ");
        satName = tleName.substr(0, delimiterPos1);
        // condition can only hold if there's more after whitespace as tleName was trimmed
        if (delimiterPos2 != std::string::npos) satName += tleName.substr(delimiterPos2 + 1, std::string::npos);
        satNum = std::stoi(tleName.substr(delimiterPos1 + 1, delimiterPos2));
    }
    else if (std::regex_match(tleName, format2))
    {
        int delimiterPos1 = tleName.find(" ");
        int delimiterPos2 = delimiterPos1 + 1 + tleName.substr(delimiterPos1 + 1, std::string::npos).find(" ");
        satName = tleName.substr(0, delimiterPos1);
        // condition can only hold if there's more after whitespace as tleName was trimmed
        if (delimiterPos2 > delimiterPos1 && delimiterPos2 != std::string::npos) satName += tleName.substr(delimiterPos2 + 1, std::string::npos);
        satNum = std::stoi(tleName.substr(delimiterPos1 + 1, delimiterPos2));
    }
    // assume uniqueness of unnumbered satellites -> all get num 1
    else if (std::regex_match(tleName, format3))
    {   
        satName = tleName;
        satNum = 1;
    }
    else 
    {
        throw cRuntimeError("Unexpected satellite name format!: \"%s\"", tleName.c_str());
    }

    // remove whitespaces for easier parsing of module names
    while(true)
    {
        int pos = satName.find(" ");
        if (pos == std::string::npos) break;
        else satName.erase(pos, 1);
    }

    return std::pair<std::string, unsigned int>(satName, satNum); 
}

void SatelliteInserter::createSatellite(TLE tle, unsigned int satNum, unsigned int vectorSize, std::string constellation) {    
    cModule* parentmod = getParentModule();
    if (!parentmod) throw cRuntimeError("Parent Module not found");

    cModuleType* satType = cModuleType::get(satelliteModuleType.c_str());
    if (!satType) throw cRuntimeError("Module Type \"%s\" not found", satelliteModuleType.c_str());

    #if OMNETPP_BUILDNUM >= 1525
        parentmod->setSubmoduleVectorSize(("leo" + constellation).c_str(), vectorSize);
        cModule* mod = satType->create(("leo" + constellation).c_str(), parentmod, satNum);
    #else
        // TODO: this trashes the vectsize member of the cModule, although nobody seems to use it
        cModule* mod = satType->create(("leo" + constellation).c_str(), parentmod, vectorSize, satNum);
    #endif

    mod->finalizeParameters();
    mod->buildInside();
    std::vector<SGP4Mobility*> sgp4Mobility = veins::getSubmodulesOfType<SGP4Mobility>(mod);
    if (sgp4Mobility.size() == 0){
        throw cRuntimeError("No mobility submodules found for Satellite module. Have you set the *.leo*[*].mobility.typename to SGP4Mobility?");
    }
    for (auto sm : sgp4Mobility) {
        sm->preInitialize(tle, wall_clock_sim_start_time_utc);
    }
    mod->scheduleStart(simTime());
    mod->callInitialize();
}

void SatelliteInserter::createSatellite(std::string traceFilePath, unsigned int satNum, unsigned int vectorSize, std::string constellation)
{
    cModule* parentmod = getParentModule();
    if (!parentmod) throw cRuntimeError("Parent Module not found");

    cModuleType* satType = cModuleType::get(satelliteModuleType.c_str());
    if (!satType) throw cRuntimeError("Module Type \"%s\" not found", satelliteModuleType.c_str());

    #if OMNETPP_BUILDNUM >= 1525
        parentmod->setSubmoduleVectorSize(("leo" + constellation).c_str(), vectorSize);
        cModule* mod = satType->create(("leo" + constellation).c_str(), parentmod, satNum);
    #else
        // TODO: this trashes the vectsize member of the cModule, although nobody seems to use it
        cModule* mod = satType->create(("leo" + constellation).c_str(), parentmod, vectorSize, satNum);
    #endif

    mod->finalizeParameters();
    mod->buildInside();
    std::vector<KeplerMobility*> keplerMobility = veins::getSubmodulesOfType<KeplerMobility>(mod);
    if (keplerMobility.size() == 0){
        throw cRuntimeError("No mobility submodules found for Satellite module. Have you set the *.leo*[*].mobility.typename to KeplerMobility?");
    }
    for (auto km : keplerMobility) {
        km->preInitialize(traceFilePath);
    }
    mod->scheduleStart(simTime());
    mod->callInitialize();
}

unsigned int SatelliteInserter::determineVectorSize(std::string constellation, unsigned int satNum) 
{    
    if (constellation == "STARLINK") {
        starlinkVectorSize = std::max(starlinkVectorSize, satNum + 1);
        return starlinkVectorSize;
    }
    if (constellation == "IRIDIUM") {
        iridiumVectorSize = std::max(iridiumVectorSize, satNum + 1);
        return iridiumVectorSize;
    }
    if (constellation == "ORBCOMM") {
        orbcommVectorSize = std::max(orbcommVectorSize, satNum + 1);
        return orbcommVectorSize;
    }
    if (constellation == "SPACEBEE") {
        spacebeeVectorSize = std::max(spacebeeVectorSize, satNum + 1);
        return spacebeeVectorSize;
    }
    if (constellation == "SPACEBEENZ") {
        spacebeenzVectorSize = std::max(spacebeenzVectorSize, satNum + 1);
        return spacebeenzVectorSize;
    }
    if (constellation == "ONEWEB") {
        onewebVectorSize = std::max(onewebVectorSize, satNum + 1);
        return onewebVectorSize;
    }
    if (constellation == "GLOBALSTAR") {
        globalstarVectorSize = std::max(globalstarVectorSize, satNum + 1);
        return globalstarVectorSize;
    }
    if (ignoreUnknownSatellites) {
        // Satellites whose name does not start with a constellation name will be discarded.
        return -1;
    }
    // Use catalog number for satellites that could not be assign to a constellation
    satelliteVectorSize = std::max(satelliteVectorSize, satNum + 1);
    return satelliteVectorSize;    
}

void SatelliteInserter::instantiateSatellite(TLE tle)
{
    std::pair<std::string, unsigned int> satellite = getConstellationAndSatNum(tle.get_satellite_name());
    unsigned int vectorSize = determineVectorSize(satellite.first, satellite.second);
    createSatellite(tle, satellite.second, vectorSize , satellite.first);
}

void SatelliteInserter::instantiateSatellite(std::string traceFilePath)
{
    std::ifstream traceFile = std::ifstream(traceFilePath);

    std::string firstLineStr; 
    std::getline(traceFile, firstLineStr);
    traceFile.close();

    std::pair<std::string, unsigned int> satellite = getConstellationAndSatNum(firstLineStr);
    unsigned int vectorSize = determineVectorSize(satellite.first, satellite.second);
    createSatellite(traceFilePath, satellite.second, vectorSize, satellite.first); 
}

void SatelliteInserter::finish()
{
}
