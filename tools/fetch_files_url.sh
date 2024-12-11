#!/bin/bash
VERSION="v1_10_01"

RUN_P1=$1
RUN_P2=$2
RUN_P3=$3

HOME_PATH=pwd

SOURCE_PATH="/pnfs/sbnd/archive/sbn/sbn_nd/data/raw/commissioning/"$VERSION"/sbnd_daq_"$VERSION"/daq/00/"$RUN_P1"/"$RUN_P2"/"$RUN_P3 # Path to the cache/tape
DESTINATION_PATH="/exp/sbnd/data/users/jbateman/workdir/crt/run/temp/$RUN_P1$RUN_P2$RUN_P3/rawdaq/" # Path to a persistent directory

cd $DESTINATION_PATH

ls $SOURCE_PATH >> temp_files.list
while read line; do
    URL=$(samweb get-file-access-url $line)
    echo $URL
    ifdh cp -D $URL .
done < temp_files.list
ls -l .
cd -
