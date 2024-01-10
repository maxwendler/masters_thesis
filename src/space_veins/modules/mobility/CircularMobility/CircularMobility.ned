package space_veins.modules.mobility.CircularMobility;

import inet.mobility.base.MovingMobilityBase;

//
// Mobility module for spacecrafts based on Kepler orbit model.
//
simple CircularMobility extends MovingMobilityBase
{
    parameters:
        @class(space_veins::CircularMobility);
        @display("i=block/cogwheel");
        @signal[mobilityStateChanged](type=inet::MobilityBase);
        int circlePlane2ndPointHalfOrbitTenth = default(9);
        string circlePlanePointsSource = default("tle");
}