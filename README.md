# MinION live basecall utilities

* nanopore_watchdog.py - Watchdog that monitoring MinKnow created directory structure
* run_albacore.sh - Wrapper to run Albacore

## Basic usage
0. To be implemented:

 - 0.1 start watchdog on the desktop
 
 - 0.2 start the MinKnow run
 
1. start watchdog script on the cluster (ionode.q prefered)
```
python3  ~/nanopore_live_basecall/nanopore_watchdog.py  -i fast5/ -c 'qsub -N log -cwd -V -b y -l mem_free=5G,h_rt=2:00:00 -pe OpenMP 8 ~/nanopore_live_basecall/run_albacore.sh {}'
```
2. start to copy files from a desktop using scp (rsync does not work)

## Limitations (To be fixed)
* transfer must be done with scp - Rsync does not produce signal compatible with watchdog package.
* transfer must be done on the desktop - Integrate the scp command into the server side script?
* transfer is currently done on a finished run - use watchdog script on the desktop to monitor MinKnow
