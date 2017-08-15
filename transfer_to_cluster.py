#!/usr/bin/env python

"""A simple python script template.

"""

import os
import sys
import argparse


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('inFolder', help="Input file", type=argparse.FileType('r'))

    args = parser.parse_args(arguments)


    ##1. compress
    ##2. rsync to server
    ##3. register into MangoDB
    
    print args
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
