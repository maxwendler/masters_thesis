import re
import astropy.units as u
from astropy.time import Time
import configparser
from datetime import datetime
import argparse
import os
from pathlib import Path

def parse_time_val(val_str: str) -> u.Quantity:
    """
    Parses a str of the format [number][unit of time] or ${[some string]=[number]}[unit of time] into a astropy.units.Quantity instance of the given unit.
    Supports milliseconds(ms), seconds(s), minutes(m/min), hours(h).
    """
    if val_str.startswith("$"):
        timelimitval_pattern = r'\${[^}]*=(\d+)[^}]*}([a-zA-Z]+)'
    else:
        timelimitval_pattern = r'(\d+)([a-zA-Z]+)'
    
    match = re.match(timelimitval_pattern, val_str)       
    if not match:
        raise ValueError("Given str does not match one of the assumed formats [number][unit] or ${sim-time-limit=[number]}[unit].")
    
    number_str = match.group(1)
    number = float(number_str)
    
    unit_str = match.group(2)
    if unit_str not in ['ms', 's', 'm', 'min', 'h']:
        raise ValueError('sim-time-limit and updateInterval in the omnetpp.ini needs to be configured by using one of the units ms, s, m/min (minutes), h !')
    unit_str = 'min' if unit_str == 'm' else unit_str
    unit = getattr(u, unit_str)

    return (number << unit)

def parseomnetini(omnetinipath: str, config: str) -> tuple[u.Quantity, u.Quantity, Time]:
    """
    Parses values of 'sim-time-limit', '*.leo*[*].mobility.updateInterval' and "*.satelliteInserter.wall_clock_sim_start_time_utc" 
    from omnetpp.ini at given path, where values of the configuration given by 'config' param overwrite values of the 'General' section.
    Returns sim-time-limit, updateInterval as astropy.units.Quantity instances with units of time.

    Requires the values to have one of the following units: milliseconds(ms), seconds(s), minutes(m/min), hours(h).
    """

    config_parser = configparser.ConfigParser()
    config_parser.read(omnetinipath)

    # find config section with given name, where 'Config' part of name is optional
    # see https://doc.omnetpp.org/omnetpp/manual/#sec:config-sim:named-configurations
    config_section = None
    if config:
        config_name = config.replace("Config ","")
        for s in config_parser.sections():
            if config_name == s.replace("Config ", ""):
                config_section = s
                break
    
    # default: no defaults, hence needs to be set in omnetpp.ini, hence exception at end of function
    timelimit = None
    wall_clock_str = None
    # default value as specified by INET: https://doc.omnetpp.org/inet/api-current/neddoc/inet.mobility.base.MovingMobilityBase.html
    updateinterval = (0.1 << u.s)

    # read general parameters, which might be overwritten by the ones of a specific configuration specified by 'config' param
    if "sim-time-limit" in config_parser["General"]:
        timelimit = parse_time_val(config_parser["General"]["sim-time-limit"])
    if "*.leo*[*].mobility.updateInterval" in config_parser["General"]:
        updateinterval = parse_time_val(config_parser["General"]["*.leo*[*].mobility.updateInterval"])
    if "*.satelliteInserter.wall_clock_sim_start_time_utc" in config_parser["General"]:
        wall_clock_str = config_parser["General"]["*.satelliteInserter.wall_clock_sim_start_time_utc"]

    if config_section:
        # read parameters of parent configurations of the configuration specified by 'config' param
        # if both set the same attributes, the conflict is simply resolved by overwriting the values set by 
        # previous parents, i.e. the ones that come later in the list of the "extends" setting 
        if "extends" in config_parser[config_section]:
            extended_configs = list(map(lambda x: x.strip(), config_parser[config_section]["extends"].split(",")))
            extended_configs.reverse()
            for c in extended_configs:
                section = None
                # Deal with fact that 'Config' keywords is not required in name of a configuration, but might occur
                try:
                    section = config_parser[c]
                except:
                    section = config_parser[f"Config {c}"]
                if "sim-time-limit" in section:
                    timelimit = parse_time_val(section["sim-time-limit"])
                if "*.leo*[*].mobility.updateInterval" in section:
                    updateinterval = parse_time_val(section["*.leo*[*].mobility.updateInterval"])
                if "*.satelliteInserter.wall_clock_sim_start_time_utc" in section:
                    wall_clock_str = section["*.satelliteInserter.wall_clock_sim_start_time_utc"]

        # read parameters of the configuration specified by 'config' param, overwriting all previously set values
        if "sim-time-limit" in config_parser[config_section]:
            timelimit = parse_time_val(config_parser[config_section]["sim-time-limit"])
        if "*.leo*[*].mobility.updateInterval" in config_parser[config_section]:
            updateinterval = parse_time_val(config_parser[config_section]["*.leo*[*].mobility.updateInterval"])
        if "*.satelliteInserter.wall_clock_sim_start_time_utc" in config_parser[config_section]:
            wall_clock_str = config_parser[config_section]["*.satelliteInserter.wall_clock_sim_start_time_utc"]

    else:
        if config:
            print(f"The given configuration {config} does not exist. Only using values from 'General' section.")

    if timelimit is None:
        raise LookupError("omnetpp.ini must set 'sim-time-limit'")
    if wall_clock_str is None:
        raise LookupError("omnetpp.ini must set 'wall_clock_sim_start_time_utc'")

    wall_clock_datetime = datetime.strptime(wall_clock_str, '"%Y-%m-%d-%H-%M-%S"')
    wall_clock_time = Time(wall_clock_datetime, format='datetime', scale='utc')

    print(f"parsed sim-time-limit: {timelimit}")
    print(f"parsed updateInterval: {updateinterval}")
    print(f"parsed wall_clock_sim_start_time_utc: {wall_clock_time}")
    return timelimit, updateinterval, wall_clock_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="parseomnetini.py", description="Prints simulation timelimit, satellite update interval and utc start time for given config of omnetpp.ini.")
    parser.add_argument("omnetini_path")
    parser.add_argument("config")
    parser.add_argument("output_path")
    args = parser.parse_args()

    timelimit, updateInterval, wall_clock_time = parseomnetini(args.omnetini_path, args.config)
    
    # format for .txt
    params_str = "\n".join(["timelimit,"+str(timelimit.value), "updateInterval,"+str(updateInterval.value), "wall_clock_time,"+str(wall_clock_time)])

    with open(args.output_path, "w") as params_file:
        params_file.writelines(params_str)

    print(f"Write params file at {args.output_path}.") 