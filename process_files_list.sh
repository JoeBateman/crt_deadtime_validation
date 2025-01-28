#!/bin/bash

VERSION="v1_10_03"

RUN=017985
echo "Run number: "$RUN
RUN_P1=${RUN:0:2}
RUN_P2=${RUN:2:2}
RUN_P3=${RUN:4:3}


N_files=1 # Number of files to process, set to -1 to process all files
BATCH_SIZE=25 # Number of files to process in each batch

# FCLS:
# decode:   run_crt_ptb_tdc_decoder_sbnd.fcl  Decodes the CRT, PTB and TDC data. Versions also exist without PTB/TDC or with PMT / TPC.
# reco:     run_crtreco_data.fcl              Runs the CRT reconstruction chain.
# ana:      run_crtana_data.fcl               Runs the CRTAnalysis module
START_STAGE="decode"

# Can either use the persistent path, or make a copy into /exp/sbnd/data. The latter is useful if there is worry that data will be moved to tape

# Using the persistent path: 
INITIAL_FILE_LIST="/exp/sbnd/app/users/jbateman/workdir/crt/crt_deadtime_validation/output_files/$RUN_P1$RUN_P2$RUN_P3/to_decode.list"

# Paths for where to store the output files of each stage
TEMP_PATH="/exp/sbnd/data/users/jbateman/workdir/crt/run/temp/$RUN_P1$RUN_P2$RUN_P3" # Path to temporarily store artroot files
FILE_LIST_PATH="./output_files/$RUN_P1$RUN_P2$RUN_P3" # Path to store the file list (can't be stored on scratch for some reason)
OUTPUT_PATH="$DATA/crt/run/$RUN_P1$RUN_P2$RUN_P3" # Path to store the final output file (could also use persistent!)

# Create the output directory if it doesn't exist
mkdir -p "$TEMP_PATH"
mkdir -p "$FILE_LIST_PATH"
mkdir -p "$OUTPUT_PATH"

# Check for the starting stage argument

if [ "$START_STAGE" == "decode" ] || [ -z "$START_STAGE" ]; then
    # Use the decode stage for run_fcl_batch.sh
    echo "Running decode stage"
    . ./tools/run_fcl_batch_list.sh "decode" $INITIAL_FILE_LIST $TEMP_PATH $FILE_LIST_PATH $N_files
fi

if [ "$START_STAGE" == "reco" ] || [ "$START_STAGE" == "decode" ] || [ -z "$START_STAGE" ]; then
    # Use the reco stage for run_fcl_batch.sh
    echo "Running reco stage"
    . ./tools/run_fcl_batch_list.sh "reco" $FILE_LIST_PATH/files_decode.list $TEMP_PATH $FILE_LIST_PATH $N_files
    . ./tools/split_reco_file_lists.sh $FILE_LIST_PATH"/files_reco.list" $BATCH_SIZE

fi


if [ "$START_STAGE" == "ana" ] || [ "$START_STAGE" == "reco" ] || [ "$START_STAGE" == "decode" ] || [ -z "$START_STAGE" ]; then
    # Use the file list from the reco stage to create the final output!
    echo "Running ana stage"

    for split_file in ${FILE_LIST_PATH}/files_reco.list_part_*; do
        echo "Processing $split_file"
        part_name=${split_file##*_}
        # Add your processing commands here, for example:
        echo "Processing "$part_name
	lar -c run_crtana_data.fcl -S $split_file -T $OUTPUT_PATH"/crtana_data_$(basename  $part_name).root"
    done


    # lar -c run_crtana_data.fcl -S $FILE_LIST_PATH"/files_reco.list" -T $OUTPUT_PATH"/crtana_data.root"

fi
