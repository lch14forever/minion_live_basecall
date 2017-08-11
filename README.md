# MinION live basecall utilities

* nanopore_watchdog.py - Watchdog that monitoring MinKnow created directory structure
* run_albacore.sh - Wrapper to run Albacore

## Basic usage
1. start the watchdog script on the desktop
```
python3 nanopore_watchdog.py -i /home/csb5/database/Minion/data/reads -l N057 -c 'SOME_TRANSFER_SCRIPT {}'
```
2. start the MinION run
3. stop MinION run
4. **TO BE AUTOMATED** create a signal in the "reads/" folder (LIBRARY_ID.SUCCESS)
5. **TO BE AUTOMATED** stop the watchdog 

## Dependency
* Linux OS (Tested with Ubuntu 16.04)
* rsync
* Python 3
** watchdog


