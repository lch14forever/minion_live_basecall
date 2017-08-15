#!/usr/bin/env python3

"""
Nanopore watchdog for live reads handling.

"""
__author__ = "Chenhao Li"
__copyright__ = "Copyright 2017, Genome Institute of Singapore"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Chenhao Li"
__email__ = "lich@gis.a-star.edu.sg"
__status__ = "Dev"

import os
import sys
import argparse
import time
import subprocess
import pickle
from glob import glob
from watchdog.observers import Observer  
from watchdog.events import FileSystemEventHandler

## global variables
FILE_PER_FOLDER=4000

def getext(filename):
    "Get the file extension"
    file_ext = filename.split(".")[-1]
    return file_ext

class MyHandler(FileSystemEventHandler):
    def __init__(self, toProcess_dir, processed_dir, cmd, library, observer):
        self.toProcess_dir = toProcess_dir ## dictionary of folders as keys and fast5 files inside as values
        self.processed_dir = processed_dir ## list of folders
        self.cmd = cmd
        self.library = library
        self.observer = observer
        super(FileSystemEventHandler, self).__init__()

    def get_dict(self):
        return {'toProcess':self.toProcess_dir, 'processed':self.processed_dir}
        
    def process(self, event):
        global FILE_PER_FOLDER
        if event.event_type=='created':
            ## ::DEBUG::
            # print(self.toProcess_dir)
            event_src = event.src_path
            bs = os.path.basename(event_src)
            ext = getext(event_src)
            if self.library in event_src:
                ## created a folder/file belongs to this library
                if event.is_directory:
                    if bs.isdigit():
                        ## sub dir created, add dict entry
                        self.toProcess_dir[event_src] = []
                        print('Created dir {} ...'.format(event_src))
                    else:
                        print('Created root dir {} ...'.format(event_src))

                elif not event.is_directory and ext=='fast5':
                    event_dir = os.path.dirname(event_src)
                    if 'mux_scan' in bs:
                        print('Detected mux_scan dir {} (will not basecall) ...'.format(event_dir))
                        ##! do nothing to mux scan reads ! -- ## FIXME: might want to fix this
                        self.toProcess_dir.pop(event_dir, None)
                    else:
                        self.toProcess_dir[event_dir] += [event_src]
                        if len(self.toProcess_dir[event_dir]) == FILE_PER_FOLDER: 
                            ## run command
                            tmp = subprocess.check_output(self.cmd.format(event_dir), shell = True)
                            print('Submitted dir {} ...'.format(event_dir))
                            del self.toProcess_dir[event_dir] ## FIXME: this is affected by slow I/O
                            self.processed_dir += [event_dir]
                elif not event.is_directory and ext=='SUCCESS':
                    ## sequencing run is done
                    if len(self.toProcess_dir) == 0:
                        print('[Finishing] Nothing to submit')
                    elif len(self.toProcess_dir) == 1:
                        event_src = list(self.toProcess_dir.keys())[0]
                        tmp = subprocess.check_output(self.cmd.format(event_src), shell = True)
                        print('[Finishing] Submitted final dir {} ...'.format(event_src))
                    else:
                        ## this should not happen ...
                        sys.stderr.write("WARNING: Multiple directories have less than 4000 reads: \n" + ' '.join(self.toProcess_dir.keys()) + '\n')
                        sys.stderr.write("Proceed anyways...\n")
                        for k in self.toProcess_dir:
                            tmp = subprocess.check_output(self.cmd.format(k), shell = True)
                            print('[Finishing] Submitted final dirs {} ...'.format(k))
                    self.toProcess_dir = dict()
                    self.processed_dir = []
                    ## find a way to exit
                    self.observer.stop()
                        
    def on_created(self, event):
        self.process(event)

def syn_dir(intermediate_dict, cmd):
    global FILE_PER_FOLDER
    full_dirs = []
    for k in intermediate_dict:
        intermediate_dict[k] = glob(k + '/*.fast5')
        if len(intermediate_dict[k]) == FILE_PER_FOLDER:
            full_dirs += [k]
    for k in full_dirs:            
        tmp = subprocess.check_output(cmd.format(k), shell = True)            
        print('Updating folders -- submitted full dir {} ...'.format(k))
        del intermediate_dict[k] ## FIXME: this is affected by slow I/O
    return intermediate_dict
        

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--inFolder",
                        default='./',
                        help="Folder to monitor [default: './']")
    parser.add_argument("-l", "--library",
                        help="Library ID to monitor")
    parser.add_argument("-c", "--cmd",
                        default="echo {}",
                        help="Command to run on each subfolder [default: 'echo {0}']")
    # parser.add_argument("--aflag",
    #                     action = "store_false",
    #                     dest="a_flag",
    #                     help="flag")
    # parser.add_argument('-o', '--outfile', help="Output file",
    #                     default=sys.stdout, type=argparse.FileType('w'))

    args = parser.parse_args(arguments)

    intermediate_file = args.inFolder+'/.'+ args.library +'.WatchDog_BK.pkl'
    if os.path.exists(intermediate_file):
        with open(intermediate_file, 'rb') as f:
            intermediate_dict = pickle.load(f)
    else:
        intermediate_dict = {'toProcess':dict(), 'processed':[] }

    print("Syncronizing existing files...")
    intermediate_dict['toProcess'] = syn_dir(intermediate_dict['toProcess'], args.cmd)
    print("Done")

    print("Watchdog ready! MinION run can be started... (Press Ctrl+C to exit...)")
    observer = Observer()
    event_handler = MyHandler(intermediate_dict['toProcess'], intermediate_dict['processed'], args.cmd, args.library, observer)
    observer.schedule(event_handler, path=args.inFolder, recursive=True)
    observer.start()
    try:
        while True:
            ## backup process every 30s
            with open(intermediate_file, 'wb') as f:
                pickle.dump(event_handler.get_dict(), f, protocol=pickle.HIGHEST_PROTOCOL)
            time.sleep(30)
    except KeyboardInterrupt:
        if observer.is_alive():
            print("Existing...")
            observer.stop()
        else:
            print("Succeeded!")
            if os.path.exists(intermediate_file):
                os.remove(intermediate_file)
    observer.join()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
