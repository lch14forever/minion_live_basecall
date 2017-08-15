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

process=None

def add_file_in(btn):
    global SRC
    SRC = app.directoryBox('Source folder', './')
    ##SRC = askdirectory()
    app.setEntry('pathin', SRC)
    
def beginMonitor(btn):
    global SRC
    global LIB
    global process
    script_dir = os.path.dirname(os.path.realpath(__file__))
    LIB = app.getEntry('lib')
    process = subprocess.Popen([script_dir+'/nanopore_watchdog.py', '-i', SRC, '-l', LIB])


def stopMonitor(btn):
    global SRC
    global process
    os.kill(process.pid, signal.SIGINT)

    
app = gui()

app.showSplash("Woof! Woof! Woof! Watchdog starting", fill="grey", stripe="#ADDFAD", fg="white", font=44)
app.setTitle("Nanopore monitor in real-time")
##app.setIcon("icon.png")
##app.setGeometry(400, 300)
app.setResizable(canResize=True)


app.setSticky("ew")
app.setStretch("column")

app.addEntry('pathin', 0, 0, 2)
app.setEntryDefault('pathin', 'Source folder')
app.addButton('Choose source folder', add_file_in, 0, 2)

app.addLabel("lib","Library name (eg. N053)",1,0,2)
app.addEntry("lib",1,2,2)



# Begin Backup section
app.addButton("Start", beginMonitor,2,0,2)
app.addButton("Stop", stopMonitor,2,2,2)
app.go()
