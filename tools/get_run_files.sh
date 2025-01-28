#!/bin/bash
VERSION="v1_10_03"

RUN=$1 # Run number, eg 17985
echo "Run number: "$RUN
RUN_P1=${RUN:0:2}
RUN_P2=${RUN:2:2}
RUN_P3=${RUN:4:3}

# Using the persistent path:                                                                                  

# The old commissioning path                                                                
# SOURCE_PATH="/pnfs/sbnd/archive/sbn/sbn_nd/data/raw/commissioning/"$VERSION"/sbnd_daq_"$VERSION"/daq/00/"$RUN_P1"/"$RUN_P2"/"$RUN_P3 # Path to the raw DAQ files               
# Current beam-on path
SOURCE_PATH="/pnfs/sbnd/archive/sbn/sbn_nd/data/raw/bnbzerobias/v1_10_03/sbnd_daq_v1_10_03/daq/00/"$RUN_P1"/"$RUN_P2"/"$RUN_P3
FILE_LIST=$(find "$SOURCE_PATH" -type f)

LIST_PATH="/exp/sbnd/app/users/jbateman/workdir/crt/crt_deadtime_validation/output_files/"$RUN_P1$RUN_P2$RUN_P3"/"

# Check if the directory exists, if not create it
[ -d $LIST_PATH ] ||
    mkdir $LIST_PATH
> $LIST_PATH"to_decode.list"
for FILE in $(echo "${FILE_LIST}")
do
    if [[ $FILE == *"strmBNBZeroBias"* ]]; then
    #  echo $(samweb -e sbnd get-file-access-url $FILE --schema xroot) >> "to_decode.list"
    #  echo $(samweb -e sbnd locate-file $FILE)/$FILE  >> "to_decode.list"
    # input=$(samweb -e sbnd locate-file $FILE)/$FILE
    echo $FILE >> $LIST_PATH"to_decode.list"
    
    fi
    #
done
