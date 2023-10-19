# Adapted from https://github.com/poliastro/poliastro/blob/main/contrib/satgpio.py
"""
The MIT License (MIT)

Copyright (c) 2012 Juan Luis Cano Rodríguez, Jorge Martínez Garrido, and the poliastro development team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import httpx
from datetime import datetime
import pytz
import os

def _generate_url(catalog_number, international_designator, name, group):
    params = {
        "GROUP": group,
        "CATNR": catalog_number,
        "INTDES": international_designator,
        "NAME": name,
    }
    param_names = [
        param_name
        for param_name, param_value in params.items()
        if param_value is not None
    ]
    if len(param_names) != 1:
        raise ValueError(
            "Specify exactly one of catalog_number, international_designator, name or group"
        )
    param_name = param_names[0]
    param_value = params[param_name]
    url = (
        "https://celestrak.org/NORAD/elements/gp.php?"
        f"{param_name}={param_value}"
        "&FORMAT=tle"
    )
    return url


def load_gp_from_celestrak(
    *, catalog_number=None, international_designator=None, name=None, group=None, dirpath="./tles"
):
    """Load general perturbations in TLE format from Celestrak.

    Returns
    -------
    Multi-line String with list of TLEs, each having three lines.
    """
    # Assemble query, raise an error if malformed
    url = _generate_url(catalog_number, international_designator, name, group)

    # utc time as used in omnetpp.ini
    datetime_of_request_str = datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%d-%H-%M-%S")
    response = httpx.get(url)
    response.raise_for_status()

    if response.text == "No GP data found":
        raise ValueError(
            f"Query '{url}' did not return any results, try a different one"
        )
    
    # else: response.text is list of tles
    # -> save as .txt
    
    # create file name
    fname = None
    if catalog_number:
        fname = str(catalog_number)
    elif international_designator:
        fname = international_designator
    elif name:
        fname = name
    elif group:
        fname = group
    fname += "_" + datetime_of_request_str + ".txt"

    # create ./tles dir if it does not exist
    try:
        os.makedirs(dirpath)
    except FileExistsError:
        pass

    # write to ./tles dir
    path = dirpath + fname
    with open(path, 'w') as tle_f:
        tle_f.write(response.text)
        print("Wrote TLE list to", path)
    
    return response.text, datetime_of_request_str


def print_sat(sat, name):
    return 0

def fetch_current_default_tles():
    # utc string as used in omnetpp.ini
    datetime_str_of_first_request = datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%d-%H-%M-%S")
    dir_path = f'./tles/requested at {datetime_str_of_first_request}/'
    load_gp_from_celestrak(group='iridium-NEXT', dirpath=dir_path)
    load_gp_from_celestrak(group='starlink', dirpath=dir_path)
    load_gp_from_celestrak(group='oneweb', dirpath=dir_path)
    load_gp_from_celestrak(group='satnogs', dirpath=dir_path)
    load_gp_from_celestrak(group='cubesat', dirpath=dir_path)

if __name__ == "__main__":
    fetch_current_default_tles()