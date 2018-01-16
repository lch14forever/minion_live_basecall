#!/usr/bin/env python3

"""MinION data handler at GIS (CSB5)
"""

import os
import sys
import argparse
import subprocess
import pymongo
import yaml
import time
import tarfile
import hashlib
import paramiko

MONGO_CFG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mongo.yaml')
CLUSTER_CFG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cluster.yaml')

CFG_1D2 = {
    kit:["SQK-LSK308"],
    flowcell:["FLO-MIN107"]
}

def transfer_file(source_file, cluster_cfg, dryrun):
    source_basename = os.path.basename(source_file)
    target_folder = cluster_cfg['data_path']
    target_folder +=  '/' + cluster_cfg['libid'] + '/'   ## cluster path spec -- assuming linux
    target_file = target_folder + source_basename
    if(dryrun):
        return target_file
    # ## windows
    if (sys.platform.startswith('win')):
        host = cluster_cfg['host']
        port = 22
        transport = paramiko.Transport((host, port))
        transport.connect(username=cluster_cfg['user'], password=cluster_cfg['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            tmp=sftp.stat(target_folder) ## Initially the folder need to be created
        except IOError:
            sftp.mkdir(target_folder)
        sftp.put(source_file, target_file)
        sftp.close()
        transport.close()
        os.remove(source_file)
    else:
    ## Linux or Mac use rsync
        login = ''.join([cluster_cfg['user'],"@", cluster_cfg['host'], ":"])
        cmd = ' '.join(['rsync -az --remove-source-files --chmod=a+rx ',
                        source_file , login + target_folder]) ## list does not work?
        tmp = subprocess.check_output(cmd, shell=True)
    return target_file 

def insert_muxjob(connection, mux, job):
    """Insert records into minion_tar_notification collection
    """
    try:
        db = connection.gisds.minion_tar_notification
        _id = db.insert_one(job)
        job_id = _id.inserted_id
        ##sys.stderr.write("Job inserted for {}\n".format(mux))
    except pymongo.errors.OperationFailure:
        sys.stderr.write("mongoDB OperationFailure\n")
        sys.exit(1)

        
def mongodb_conn(use_test_server=False):
    """Return connection to MongoDB server"""
    global MONGO_CFG_FILE
    with open(MONGO_CFG_FILE, 'r') as stream:
        try:
            mongo_conns = yaml.load(stream)
        except yaml.YAMLError as exc:
            sys.stderr.write("Error in loading {}\n".format(MONGO_CFG_FILE))
            raise
    if use_test_server:
        constr = mongo_conns['test']
    else:
        constr = mongo_conns['production']
    try:
        connection = pymongo.MongoClient(constr)
    except pymongo.errors.ConnectionFailure:
        sys.stderr.write("Could not connect to the MongoDB server\n")
        return None
    ##sys.stderr.write("Database connection established\n")
    return connection
        
def make_tarfile(source_dir, dryrun):
    """
    create a tar file from a directory
    """
    target_name = source_dir.rstrip(os.sep) + '.tar.gz'
    if(dryrun):
        return [target_name, 'DryRunWithoutOutput']
    with tarfile.open(target_name, "w:gz") as tar:
        tar.dereference = True
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    hasher = hashlib.sha1()
    with open(target_name, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return [target_name, hasher.hexdigest()]

def get_minion_param(compressed_file):
    """
    get sequencing information libid, kit, flowcell
    """
    lib_path = os.path.split(os.path.dirname(compressed_file.rstrip(os.sep)))
    assert(lib_path[-1]=='fast5') ## minknow default structure
    date, time, libid, flowcell, kit = lib_path[-2].split('_')[-5:]
    return [libid, flowcell, kit]

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)    
    parser.add_argument('inFolder', help="Input folder (A folder containing fast5 files)")
    parser.add_argument('--dryrun',
                        action = "store_true",
                        dest   = "dryrun",
                        default= False,
                        help   = "Do not register to the database, print the database entry"
    )
    args = parser.parse_args(arguments)
    ## load cluster config file
    with open(CLUSTER_CFG_FILE, 'r') as stream:
        try:
            cluster_cfg = yaml.load(stream)
        except yaml.YAMLError as exc:
            sys.stderr.write("Error in loading {}\n".format(CLUSTER_CFG_FILE))
            raise
        
    ##1. compress
    ## FIXME: add error/exception handling
    source_dir = os.path.abspath(args.inFolder)
    compressed_file, tar_sha1 = make_tarfile(source_dir, args.dryrun)
    libid, flowcell, kit = get_minion_param(compressed_file)
    basecall_script = 'read_fast5_basecaller.py'
    if flowcell in CFG_1D2['flowcell'] and kit in CFG_1D2['kit']:
        basecall_script = 'full_1dsq_basecaller.py'
    ##2. rsync to server
    cluster_cfg['libid'] = libid 
    cluster_tar_path = transfer_file(compressed_file, cluster_cfg, args.dryrun)
    epoch_present = int(time.time())*1000
    ##3. register into MangoDB
    conn = mongodb_conn()
           
    record = {
        'tar'       :   cluster_tar_path,
        'conda'     :   cluster_cfg['conda_path'],
        'env'       :   cluster_cfg['conda_env'],
        'sha1'      :   tar_sha1,
        'src'       :   cluster_cfg["process_src"] + '/' + basecall_script,
        'kit'       :   kit,
        'flowcell'  :   flowcell,
        'status'    :   'unprocessed',
        'outsuffix' :   libid,### what should this be?
        'timestamp' :   epoch_present
    }
    if args.dryrun == True:
        print(record)
    else:
        tmp = insert_muxjob(conn, libid, record)

    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
