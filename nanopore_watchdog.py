#!/usr/bin/env python

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
    def __init__(self, cmd):
        self.dir_counter = dict()
        self.cmd = cmd
        super(FileSystemEventHandler, self).__init__()
    
    def process(self, event):
        if event.event_type=='created':
            if event.is_directory:
                ## sub dir created:
                ## add dict entry
                self.dir_counter[event.src_path] = 0
                print('Created dir {} ...'.format(event.src_path))
            elif getext(event.src_path)=='fast5':
                # print(file_ext) ## Rsync compress and this does not work
                event_dir = os.path.dirname(event.src_path)
                self.dir_counter[event_dir] += 1
                if self.dir_counter[event_dir] == 4000: ## FIXME: as an argument
                    ## run command
                    del self.dir_counter[event_dir]
                    tmp = subprocess.check_output(self.cmd.format(event_dir), shell = True)
                    print('Submitted dir {} ...'.format(event_dir))
                
    def on_created(self, event):
        self.process(event)


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--inFolder",
                        default='./',
                        help="Folder to monitor [default: './']")
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
    
    event_handler = MyHandler(args.cmd)
    observer = Observer()
    observer.schedule(event_handler, path=args.inFolder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
