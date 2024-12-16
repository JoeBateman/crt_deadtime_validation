run=$1
xml_run=${run#0}
echo "Processing run $run"
echo $xml_run
# project.py --xml xmls/grid_processing_$xml_run.xml --stage crt_decode --checkana 
. tools/move_files.sh $run