# MinION live basecall utilities

* nanopore_watchdog.py - Watchdog that monitoring MinKnow created directory structure
* run_albacore.sh - Wrapper to run Albacore

## Basic usage
0. start program on the server for live raw read processing (This could simply be the same nanopore_watchdog.py with the processing script)
1. start the GUI
```
python3 /home/csb5/database/Minion/Minion_softwares/minion_live_basecall/run_app.py
```
2. choose the directory to monitor, key in the library ID to watch for and click on "Start watchdog"
3. start the MinION run
3. stop the MinION run
4. click on "Stop watchdog": this will create an empty file [LIB_ID].SUCCESS in the MinKNOW working directory and let the watchdog submit the folders with less than 4000 reads (should only have 1)
5. wait for the background processes (submitted) job to finish (print a message of "Succeeded!")
6. click on "Exit watchdog": this will quit the watchdog script
7. close the GUI

## To be implemented
* Compress the folder, transfer the folder and register into the database

## Issues
* On GIS nftp file system, rsync does not seem to work (events not detected).
* On GIS nftp file system, scp *tar.gz files from local host to server does not trigger the creation event.

## Dependency
* Linux OS (Tested with Ubuntu 16.04)
* rsync
* Python 3
* Python watchdog
* python3-tk (Linux)
* Pymongo -- interacting with GIS system
