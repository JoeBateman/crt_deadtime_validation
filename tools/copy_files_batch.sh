#!/bin/bash

RUNS=("013688", "013689", "013690", "013693", "013758")

for RUN in "${RUNS[@]}"; do 
    # split run number into 3 parts
    RUN_P1=${RUN:0:2}
    RUN_P2=${RUN:2:2}
    RUN_P3=${RUN:4:2}
    echo $RUN_P1 $RUN_P2 $RUN_P3
    . /exp/sbnd/app/users/jbateman/workdir/crt/deadtime_t1/tools/fetch_files_url.sh $RUN_P1 $RUN_P2 $RUN_P3
done