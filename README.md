# CRT Deadtime Validation

This repo documents the work done for CRT deadtime validation, and contains all the tools needed to decode, reco, and analyse daq files to check CRT deadtime during beam-on periods. 

The notebook requires an installation of LArSoft (version > v09_93_01_02rc0), and care needs to be taken to match the artdaq version used to take the run with the version larsoft is using.

THIS NEEDS TO BE UPDATED TO USE THE LATEST OFFLINE CRT BRANCH

The notebook requires an installation of LArSoft and Henry Lay's branches features/hlay_crt/offline in sbndcode, sbnobj and sbncode (detailed [here](https://sbn-docdb.fnal.gov/cgi-bin/sso/RetrieveFile?docid=36812&filename=CRT%20Offline%20Guide%20v3.pdf&version=3) and in docdb-36812).

However, to use the latest daq version (v1_10_03) additional modifications need to be made. The steps are detailed below.

To decode daq files and get the CRT reco data into a root file, you can run the fcls on the gpvm, using process_files.sh or process_files_list.sh, or on the grid using project.py and modifying an xml files located in /xmls/. To get specific daq files to use, tools/get_run_files.sh can be modified/used to to generate a file list for a run and file name criteria (such as ...strmBNBZeroBias... files only). The destination can be specified using process_files.sh, and for grid jobs checkana_copy.sh can be used to generate a file list and move the ana files to a specified location.

Once the ana files are generated, you can use timing_figures.ipynb to process each file in a python notebook, or use timing_pkl_maker.py to process the .root files as a script and save them as .pkl files. This means that data does not need to be repeatedly analysed, and we can combine a large number of runs into a singular figure.

timing_plotting.ipynb can be used to read these pkl files, combining them into singular, large dataset figures.


## Getting a version of larsoft working!


### Getting products with MRB:

mrb newDev -v v09_93_01_01 -q e26:prof \
source local_producs \
mrb g sbndcode \
mrb g sbncode \
mrb g sbnobj 

Then the following need to be modified
\
#### sbnobj: 
        
    git checkout origin/feature/hlay_crt_offline

#### sbncode:
    git checkout origin/feature/hlay_crt_offline
    emacs ups/product_deps:
        line 259: sbndaq v1_10_03
    cd sbncode/Supera
    git checkout tags/icarus_v09_83_01

#### sbndcode:
    
    git checkout origin/feature/hlay_gdml_v02_03

    OR USE COMMIT 21/11/24
    git checkout 70ff2f2edf6ecee1065da709a59b595807c5f2f8




#### OLD


From a clean SL7 instance, working with sbncode v09_93_01

### Getting products with MRB:

mrb newDev -v v09_93_01 -q e26:prof \
source local_producs \
mrb g sbndcode \
mrb g sbncode \
mrb g sbnobj 

Then the following need to be modified
\
#### sbnobj: 
        
    git checkout origin/feature/hlay_crt_offline

#### sbncode:
    git checkout origin/feature/hlay_crt_offline
    emacs ups/product_deps:
        line 259: sbndaq v1_10_03
    cd sbncode/Supera
    git checkout tags/icarus_v09_83_01

#### sbndcode:
    git checkout origin/feature/hlay_gdml_v02_03
    emacs ups/product_deps:
        sbncode         v09_93_01 
    copy sbndcode/CRT/CRTAna/* from feature/hlay_crt_offline into this directory. Remove ADRIFT_module and run_adrift, which will not compile!

    This is because i ran into issues compiling feature/hlay_crt_offline, and we only really need the geometry and analysis fhicls!




