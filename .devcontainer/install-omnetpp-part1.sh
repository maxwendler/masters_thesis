#!/bin/bash

#
# Copyright (C) 2023 Christoph Sommer <sommer@cms-labs.org>
#
# Documentation for these modules is at http://veins.car2x.org/
#
# SPDX-License-Identifier: GPL-2.0-or-later
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# The following list shows changes made by Mario Franke
# Copyright (C) 2023 Mario Franke <research@m-franke.net>
# Documentation for space_Veins is at http://sat.car2x.org/
# SPDX-License-Identifier: GPL-2.0-or-later
#
# 2023-08-17 change PYTHONPATH variable because Ubuntu Jammy brings
#            python3.10
#            disable WITH_OSGEARTH

# This script needs the following environment variables to be set:
#   - OPP_VERSION: the version of OMNeT++ to install (e.g. 6.0.1)

# abort if one of the environment variables is not set
set -e

# install dependencies (needed before java will install)
apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends \
    ca-certificates \
    ca-certificates-java \
    ;

# install dependencies
# note the use of clang-13 to allow valgrind 3.19 to interoperate with binaries
apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends \
    bison \
    build-essential \
    ccache \
    clang-13 \
    curl \
    doxygen \
    flex \
    g++ \
    gcc \
    gdb \
    git \
    graphviz \
    libopenscenegraph-dev \
    libqt5opengl5-dev \
    libswt-gtk-4-java \
    libswt-webkit-gtk-4-jni \
    libxml2-dev \
    lld \
    make \
    openjdk-17-jre \
    perl \
    python3 \
    python3-matplotlib \
    python3-numpy \
    python3-pandas \
    python3-pip \
    python3-scipy \
    python3-seaborn \
    qtbase5-dev \
    libqt5svg5 \
    tcl-dev \
    tk-dev \
    wget \
    xdg-utils \
    zlib1g-dev \
    ;

# ensure xdg-utils is happy with the system
mkdir -p /usr/share/desktop-directories/

# install posix_ipc
mkdir -p /opt/pip
python3 -m pip install --root=/opt/pip posix_ipc
export PYTHONPATH=/opt/pip/usr/local/lib/python3.10/dist-packages:$PYTHONPATH
