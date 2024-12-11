#!/bin/bash
# OLD/ALT method to fetch files from the cache/tape using samweb prestage

RUNS="default_value"
RUNS=("13690", "13693", "13758") # Already have "13688" "13689" staged
nfiles=-1
for RUN in "${RUNS[@]}"; do
    echo "Processing $RUN"
    defname="test_crtana_run$RUN"
    samweb prestage-dataset -e sbnd --defname=$defname --max-files=$nfiles
    # Add your processing commands here
done