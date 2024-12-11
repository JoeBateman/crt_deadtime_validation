#!/bin/bash
# OLD/ALT method to fetch files from the cache/tape
VERSION="v1_10_01"

RUN_P1=$1
RUN_P2=$2
RUN_P3=$3

SOURCE_PATH="/pnfs/sbnd/archive/sbn/sbn_nd/data/raw/commissioning/"$VERSION"/sbnd_daq_"$VERSION"/daq/00/"$RUN_P1"/"$RUN_P2"/"$RUN_P3 # Path to the cache/tape
DESTINATION_PATH="/exp/sbnd/data/users/jbateman/workdir/crt/run/temp/$RUN_P1$RUN_P2$RUN_P3/rawdaq/" # Path to a persistent directory

cd $SOURCE_PATH
ifdh cp -r * $DESTINATION_PATH
cd -
