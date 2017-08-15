#!/usr/bin/env python3

"""Nanopore watchdog GUI

"""

from appJar import gui
import os
import sys
import subprocess
import signal

SRC=''
LIB=''
CMD='~/database/Minion/Minion_softwares/minion_live_basecall/transfer_tmp.sh {}'
##CMD='echo {}'

process=None

def add_file_in(btn):
    global SRC
    SRC = app.directoryBox('Source folder', '~/database/Minion/data/reads')
    ##SRC = askdirectory()
    app.setEntry('pathin', SRC)
    
def beginMonitor(btn):
    global SRC
    global LIB
    global process
    global CMD
    script_dir = os.path.dirname(os.path.realpath(__file__))
    LIB = app.getEntry('lib')
    cmd = [script_dir+'/nanopore_watchdog.py', '-i', SRC, '-l', LIB, '-c', CMD]
    process = subprocess.Popen(cmd)



def exitMonitor(btn):
    global SRC
    global process
    os.kill(process.pid, signal.SIGINT)

def finishMonitor(btn):
    global LIB
    global SRC
    success_flag = SRC + '/' + LIB + '.SUCCESS'
    open(success_flag, 'a').close()

    
app = gui()

app.showSplash("Woof! Woof! Woof! Watchdog starting", fill="grey", stripe="#ADDFAD", fg="white", font=44)
app.setTitle("Nanopore monitor in real-time")
##app.setIcon("icon.png")
app.setGeometry(600, 102)
app.setResizable(canResize=True)


app.setSticky("ew")
app.setStretch("column")

app.addEntry('pathin', 0, 0, 4)
app.setEntryDefault('pathin', 'Source folder')
app.addButton('Choose source folder', add_file_in, 0,6)

app.addLabel("lib","Library name (eg. N053)",1,6)
app.addEntry("lib",1,0,4)



# Begin Backup section
app.addButton("Start watchdog", beginMonitor,2,0)
app.addButton("Stop watchdog", finishMonitor,2,1)
app.addButton("Exit watchdog", exitMonitor,2,2)

app.go()
