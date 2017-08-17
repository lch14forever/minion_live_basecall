#!/usr/bin/env python3

"""Nanopore watchdog GUI

"""

from appJar import gui
import os
import sys
import subprocess
import signal

MINKNOW_WD='~/database/Minion/data/reads'
SRC=MINKNOW_WD
LIB=''
CMD='echo {}'

process=None

def add_file_in(btn):
    global SRC
    global MINKNOW_WD
    SRC = app.directoryBox('Source folder', MINKNOW_WD)
    app.setEntry('pathin', SRC)

def add_cmd_in(btn):
    global CMD
    script_dir = os.path.dirname(os.path.realpath(__file__))
    CMD = app.openBox('Sript to run', script_dir)
    CMD += ' {}'
    app.setEntry('cmdin', CMD)
    
def beginMonitor(btn):
    global SRC
    global LIB
    global process
    global CMD
    script_dir = os.path.dirname(os.path.realpath(__file__))
    LIB = app.getEntry('lib')
    cmd = [sys.executable, script_dir+'/nanopore_watchdog.py', '-i', SRC, '-l', LIB, '-c', CMD]
    process = subprocess.Popen(cmd)

def exitMonitor(btn):
    global SRC
    global process
    os.kill(process.pid, signal.SIGINT)

def finishMonitor(btn):
    global LIB
    global SRC
    success_flag = SRC + '/' + LIB + '.SUCCESS'
    open(success_flag, 'a').close() ## touch flag file

app = gui()

## Starting splash
app.showSplash("Woof! Woof! Woof! Watchdog starting", fill="grey", stripe="#ADDFAD", fg="white", font=44)

## app gui
app.setTitle("Nanopore monitor in real-time")
##app.setIcon("icon.png")
app.setGeometry(600, 140)
app.setResizable(canResize=True)
app.setSticky("ew")
app.setStretch("column")

## Directory to be monitored
app.addEntry('pathin', 0, 0, 4)
app.setEntryDefault('pathin', MINKNOW_WD)
app.addButton('Choose source folder', add_file_in, 0,6)

## Command script file selector
app.addEntry('cmdin', 1, 0, 4)
app.setEntryDefault('cmdin', CMD)
app.addButton('Choose command script', add_cmd_in, 1,6)

## Library ID entry
app.addLabel("lib","Library name (eg. N053)",2,6)
app.addEntry("lib",2,0,4)

## buttons
app.addButton("Start watchdog", beginMonitor,3,0)
app.addButton("Stop watchdog", finishMonitor,3,1)
app.addButton("Exit watchdog", exitMonitor,3,2)

app.go()
