package space_veins.modules.mobility.KeplerMobility;

import inet.mobility.base.MovingMobilityBase;

//
// Mobility module for spacecrafts based on Kepler orbit model.
//
simple KeplerMobility extends MovingMobilityBase
{
    parameters:
        @class(space_veins::KeplerMobility);
        @display("i=block/cogwheel");
        @signal[mobilityStateChanged](type=inet::MobilityBase);
}