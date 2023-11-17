#!/bin/bash

# get architecture (x86_64 or aarch64)
ARCH=$(uname -m)

# download and unpack OMNeT++ if not already done
cd /opt
if [ ! -d omnetpp-${OPP_VERSION} ]; then
    mkdir -p omnetpp-${OPP_VERSION}
    cd omnetpp-${OPP_VERSION}
    curl --location https://github.com/omnetpp/omnetpp/releases/download/omnetpp-${OPP_VERSION}/omnetpp-${OPP_VERSION}-src-linux.tgz | tar -xzv --strip-components=1
fi

cd /opt
ln -sf omnetpp-${OPP_VERSION} omnetpp

# enable ccache
export PATH=/usr/lib/ccache:$PATH

# ensure /opt/omnetpp/configure.user has WITH_OSG=yes changed to WITH_OSG=no (OMNeT++ Qtenv in Docker has problems creating OpenGL contexts, so better we don't even offer the option)
# Note: On MacOS, LIBGL_ALWAYS_INDIRECT=1 in Docker env and `defaults write org.xquartz.X11 enable_iglx -bool YES` on host are needed to run OpenGL apps like glxgears in Docker, but this is not enough for OMNeT++ Qtenv
sed -i 's/WITH_OSG=yes/WITH_OSG=no/g' /opt/omnetpp/configure.user
# disable OSG EARTH because we did not installed the dependency
sed -i 's/WITH_OSGEARTH=yes/WITH_OSGEARTH=no/g' /opt/omnetpp/configure.user

# build OMNeT++
cd /opt/omnetpp
export PATH=$PATH:/opt/omnetpp/bin
source setenv
CC=clang-13 CXX=clang++-13 ./configure
make -j$(nproc) MODE=debug
make -j$(nproc) MODE=release

# make directory world-writable (as the IDE writes to its install location)
chmod -R a+wX /opt/omnetpp/
