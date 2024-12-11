#!/bin/bash

# Check if the required arguments are provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <stage> <INPUT_DIRECTORY> <OUTPUT_DIRECTORY> <Number of Files to Process>"
    return 1
fi

STAGE="$1"
INPUT_DIRECTORY="$2"
OUTPUT_DIRECTORY="$3"
FILES_LIST_DIRECTORY="$4"
N="$5"  # Number of files to process, set to -1 to process all files


# THIS SHOULD PROBABLY TAKE A FCL AS AN ARGUMENT INSTEAD!

# FCLS:
# run_crt_ptb_tdc_decoder_sbnd.fcl  Decodes the CRT, PTB and TDC data. Versions also exist without PTB/TDC or with PMT / TPC.
# run_crtreco_data.fcl              Runs the CRT reconstruction chain.
# run_crtana_data.fcl               Runs the CRTAnalysis module

if [ "$STAGE" = "decode" ]; then
    FCL="run_crt_ptb_tdc_decoder_sbnd.fcl"
elif [ "$STAGE" = "reco" ]; then
    FCL="run_crtreco_data.fcl"
elif [ "$STAGE" = "ana" ]; then
    FCL="run_crtana_data.fcl"
else
    echo "Warning: Invalid stage $STAGE. Please specify decode, reco, or ana."
    return 1
fi

echo $FCL

OUTPUT_FILE_LIST="$FILES_LIST_DIRECTORY/files_$STAGE.list"

# Check if the directory exists
if [ ! -d "$INPUT_DIRECTORY" ]; then
    echo "Error: Directory $INPUT_DIRECTORY does not exist."
    return 1
fi

OUTPUT_DIRECTORY="$OUTPUT_DIRECTORY/$STAGE/"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIRECTORY"

# Initialize the output file list
> "$OUTPUT_FILE_LIST"

# Run a command to create an empty text file with the same name as the input file in the output directory
if [ "$N" -eq -1 ]; then
    find "$INPUT_DIRECTORY" -type f | while IFS= read -r file; do
        base_name=$(basename "$file")
        output_file="$OUTPUT_DIRECTORY${base_name%.*}_$STAGE.root"
        echo "Creating file $output_file"
        # Create an empty file with the same name as the input file in the output directory
        lar -c $FCL -s $file -o $output_file
        # Save the output file path to the output file list
        echo "$output_file" >> "$OUTPUT_FILE_LIST"
    done
else
    find "$INPUT_DIRECTORY" -type f | head -n $N | while IFS= read -r file; do
        base_name=$(basename "$file")
        output_file="$OUTPUT_DIRECTORY${base_name%.*}_$STAGE.root"
        echo "Creating file $output_file"
        # Create an empty file with the same name as the input file in the output directory
        lar -c $FCL -s $file -o $output_file
        # Save the output file path to the output file list
        echo "$output_file" >> "$OUTPUT_FILE_LIST"
    done
fi

# ls $OUTPUT_DIRECTORY  >> "$OUTPUT_FILE_LIST"

echo "Output file paths and names have been written to $OUTPUT_FILE_LIST"