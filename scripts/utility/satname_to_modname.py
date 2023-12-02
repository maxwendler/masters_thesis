import re

name_hyphen_num_re = r"(\w+-\d+(?:\s.*)*)"
name_whitespace_num_re = r"(\w+\s\d+(?:\s.*)*)"
no_num_re = r"(\w+([\s,-].*\D+.*)*)"

def satname_to_modname(satname: str) -> str:
    """
    Converts a satellite name as it occurs in TLEs to its adapted form in the OMNET++ simulation.
    """

    # adaptation in create_traces.py, or SatelliteInserter.cc when no traces are used
    satname = satname.replace("/","-")
    
    # adaptations in SatelliteInserter.cc
    satname = satname.replace(".","-")
    modname = ""

    if re.fullmatch(name_hyphen_num_re, satname):
        constellation_and_remainder = satname.split("-", maxsplit=1)
        modname = constellation_and_remainder[0]
        satnum_and_remainder = constellation_and_remainder[1].split(" ", 1)
        if len(satnum_and_remainder) > 1:
            modname += satnum_and_remainder[1]
        modname += f"[{str(int(satnum_and_remainder[0]))}]"
    
    elif re.fullmatch(name_whitespace_num_re, satname):
        constellation_and_remainder = satname.split(" ", 1)
        modname = constellation_and_remainder[0]
        satnum_and_remainder = constellation_and_remainder[1].split(" ", 1)
        if len(satnum_and_remainder) > 1:
            modname += satnum_and_remainder[1]
        modname += f"[{str(int(satnum_and_remainder[0]))}]"
    
    elif re.fullmatch(no_num_re, satname):
        modname = satname + "[1]"
    
    else:
        raise NameError(f"Format of satellite {satname} is not supported!")
    
    modname = modname.replace(" ","")
    modname = "leo" + modname

    return modname