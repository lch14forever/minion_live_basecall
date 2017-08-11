#!/usr/bin/env python3

import os
import sys
import argparse
import time
import subprocess
from watchdog.observers import Observer  
from watchdog.events import FileSystemEventHandler

def getext(filename):
    "Get the file extension"
    file_ext = filename.split(".")[-1]
    return file_ext

class MyHandler(FileSystemEventHandler):
    def __init__(self, cmd, library):
        self.dir_counter = dict()
        self.library = library
        self.cmd = cmd
        super(FileSystemEventHandler, self).__init__()
    
    def process(self, event):
        if event.event_type=='created':
            event_src = event.src_path
            bs = os.path.basename(event_src)
            ext = getext(event_src)
            if self.library in event_src:
                ## created a folder/file belongs to this library
                if event.is_directory:
                    if bs.isdigit():
                        ## sub dir created, add dict entry
                        self.dir_counter[event_src] = 0
                        print('Created dir {} ...'.format(event_src))
                    else:
                        ## directory root or root/fast5 created
                        pass
                elif not event.is_directory and ext=='fast5':
                    event_dir = os.path.dirname(event_src)
                    if 'mux_scan' in bs:
                        ##! do nothing to mux scan reads ! -- ## FIXME: might want to fix this
                        self.dir_counter.pop(event_dir, None)
                    else:
                        self.dir_counter[event_dir] += 1
                        if self.dir_counter[event_dir] == 4000: 
                            ## run command
                            tmp = subprocess.check_output(self.cmd.format(event_dir), shell = True)
                            print('Submitted dir {} ...'.format(event_dir))
                            del self.dir_counter[event_dir] ## FIXME: this is affected by slow I/O
                elif not event.is_directory and ext=='SUCCESS':
                    ## sequencing run is done
                    if len(self.dir_counter) == 0:
                        pass
                    elif len(self.dir_counter) == 1:
                        event_src = list(self.dir_counter.keys())[0]
                        tmp = subprocess.check_output(self.cmd.format(event_src), shell = True)
                        print('Submitted final dir {} ...'.format(event_src))
                    else:
                        ## this should not happen ...
                        sys.stderr.write("WARNING: Multiple directories have less than 4000 reads: \n" + ' '.join(self.dir_counter.keys()) + '\n')
                        sys.stderr.write("Proceed anyways...\n")
                        for k in self.dir_counter:
                            tmp = subprocess.check_output(self.cmd.format(k), shell = True)
                            print('Submitted final dirs {} ...'.format(k))
                        ## find a way to exit
                
    def on_created(self, event):
        self.process(event)


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

    event_handler = MyHandler(args.cmd, args.library)
    observer = Observer()
    observer.schedule(event_handler, path=args.inFolder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
