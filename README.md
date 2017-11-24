# MinION live basecall utilities

## Description

I would like to build a cross-platform framework for processing Nanopore MinION sequencing data **LIVE**. The framework should have the following properties:
1. Easy installation (I guess the requirements suggest a docker image!): 
	- [ ] Cross platform
	- [ ] Easy installation
2. User friendly
	- [x] A GUI for intiutive usage	
	- [ ] One click starup
3. Extendable (R shiny + Python watchdog + **Anything**)
    - [x] The GUI runs the watchdog script, generates indicator for completion, and stop the watchdog script.
    - [x] The watchdog takes care of MinKNOW generated files. It assumes that a folder is completed after 4000 fast5 files are generated.
    - [ ] And many more opportunities... 
    	- [x] Live basecall: script "transfer_to_cluster.py" is used for compressing the completed folder, transferring it to the cluster and informing NGSP for basecall with their framework.
    	- [ ] Live assembly?
    	- [ ] Live mapping?
    	- [ ] Live metagenomics? Real-time detection of genes, pathogens, etc.

## Usage:

Start the shiny app in terminal:

```{sh}
R -e "shiny::runApp('PATH_TO_REPO/minion_live_basecall/runApp')"
```

Access in browser at <http://127.0.0.1:XXXX> (XXXX is the port number randomly selected by Shiny), or <http://localhost:4404>.

## Known issues
1. Some problem with paramiko sftp on cluster -- potential fix with rsync?
2. Too many dependencies -- potential fix with docker?
3. Cannot send SIGINT to script on windows with python previously. Can I do it with R?
4. Seems only works on MAC OS or Linux OS now. Windows is a must since few lab people will use unix like systems.

## Dependency
* Linux OS (Tested with Ubuntu 16.04)
* rsync
* Python 3
* Python watchdog
* python3-tk (Linux)
* Pymongo -- interacting with GIS system
