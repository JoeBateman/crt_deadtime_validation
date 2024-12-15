#!/bin/bash
# For some reason larsoft only reads the fist 25 files in the list, so we need to split the list into smaller lists and cycle
# through them. This script will split the list of files into smaller lists of 25 files each.


FILES_PATH="$1"
BATCHES=$2

# Check that FILES_PATH is a valid file
if [ ! -f "$FILES_PATH" ]; then
    echo "Error: File $FILES_PATH does not exist."
    return 1
fi

# Cycle through the files in the list and split them into smaller lists of 25 files each

# Split the file into smaller lists of 25 files each
split -l $BATCHES "$FILES_PATH" "${FILES_PATH}_part_"

echo "File has been split into smaller lists of 25 files each."