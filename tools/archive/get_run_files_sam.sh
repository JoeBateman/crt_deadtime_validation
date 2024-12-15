#!/bin/bash
setup fife_utils

RUN=13689
RUN_P1=$(printf "%02d" ${RUN:0:1})
RUN_P2=${RUN:1:2}
RUN_P3=${RUN:3:2}

FILE_LIST=$(samweb -e sbnd list-definition-files sbnd_runset_$RUN_raw)


LIST_PATH="/exp/sbnd/app/users/jbateman/workdir/crt/crt_deadtime_validation/output_files/"$RUN_P1$RUN_P2$RUN_P3"/"
# Check that the directory exists, and if not, create it
[ -d $LIST_PATH ] ||
    mkdir $LIST_PATH
> $LIST_PATH"to_decode.list"

for FILE in $(echo "${FILE_LIST}")
do
    if [[ $FILE == *"strmBNBZeroBias"* ]]; then
    #  echo $(samweb -e sbnd get-file-access-url $FILE --schema xroot) >> "to_decode.list"
    #  echo $(samweb -e sbnd locate-file $FILE)/$FILE  >> "to_decode.list"
    input=$(samweb -e sbnd locate-file $FILE)/$FILE
    echo ${input#enstore:} >> $LIST_PATH"to_decode.list"
    fi
    #
done
