"""
Copyright (C) 2024 Max Wendler <max.wendler@gmail.com>

SPDX-License-Identifier: GPL-2.0-or-later

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import argparse

parser = argparse.ArgumentParser(prog="runtime_from_benchmarks.py",
                                description="""Adds and outputs runtime of benchmark files from given path.""")
parser.add_argument("output_path")
parser.add_argument("benchmark_paths", nargs="+")
args = parser.parse_args()

runtime_sec = 0
for path in args.benchmark_paths:
    with open(path, "r") as benchmark_f:
        vals_line = benchmark_f.readlines()[1]
        # use runtime from first benchmark column
        sec_val = float(vals_line.split("\t")[0])
        runtime_sec += sec_val

with open(args.output_path, "w") as out_f:
    out_f.write("\n".join(["s", str(runtime_sec)]))