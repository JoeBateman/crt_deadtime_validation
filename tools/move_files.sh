#!/bin/bash

RUN_NUMBER=$1
SBNDCODE_VERSION="v09_91_02_0201"

FILE_LIST_PATH="/pnfs/sbnd/scratch/users/jbateman/$SBNDCODE_VERSION/$RUN_NUMBER/crt_decode/filesana.list"
TARGET_DIR="/exp/sbnd/data/users/jbateman/workdir/crt/run/$RUN_NUMBER"

declare -A alphabet_map
for i in {0..25}; do
  letter=$(printf "\x$(printf %x $((i + 97)))")
  alphabet_map[$i]=$letter
done

counter_a=0
counter_b=0

while IFS= read -r file_path; do
  if [[ $counter_a == 26 ]]; then
    counter_a=0
    counter_b=$((counter_b + 1))
  fi
  suffix="${alphabet_map[$counter_b]}${alphabet_map[$counter_a]}"
  echo "crt_ana_$suffix.root"
  cp "$file_path" "$TARGET_DIR/crt_ana_$suffix.root"
  ((counter_a++))
done < "$FILE_LIST_PATH"