# CRT Deadtime Validation

This repo documents the work done for CRT deadtime validation, and contains all the tools needed to decode, reco, and analyse daq files to check CRT deadtime during beam-on periods. 

The notebook requires an installation of LArSoft and Henry Lay's branches features/hlay_crt/offline in sbndcode, sbnobj and sbncode (detailed [here](https://sbn-docdb.fnal.gov/cgi-bin/sso/RetrieveFile?docid=36812&filename=CRT%20Offline%20Guide%20v3.pdf&version=3) and in docdb-36812).

However, to use the latest daq version (v1_10_03) additional modifications need to be made. The steps are detailed below.

Firstly proces_files.sh should be edited to set file paths, daq version, run number and fcl stage to create the correctly decoded root files needed for the analysis. Then, timing_figures.ipynb can be used to process each run. For large runs, this is done in batches to reduced memory overhead. 
Once a run is processed, the required data is saved as a .pkl file, meaning multiple runs can be combined together without unneccessary reprocessing.


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




