# MinION live basecall utilities

* nanopore_watchdog.py - Watchdog that monitoring MinKnow created directory structure
* run_albacore.sh - Wrapper to run Albacore

## Basic usage
0. 
1. start the GUI
```
python3 /home/csb5/database/Minion/Minion_softwares/minion_live_basecall/run_app.py
```
2. choose the directory to monitor, key in the library name to watch for and click on "Start watchdog"
3. start the MinION run
3. stop the MinION run
4. click on "Stop watchdog": this will create an empty file [LIB_ID].SUCCESS in the MinKNOW workind directory and let the watchdog to submit the folders with less than 4000 reads (should only have 1)
5. click on "Exit watchdog": this will quit the watchdog script
6. close the GUI

## To be implemented
* Currently nothing is run for the folders
* Compress the folder, transfer the folder and register into the database


## Dependency
* Linux OS (Tested with Ubuntu 16.04)
* rsync
* Python 3
* Python watchdog
* python3-tk (Linux)

