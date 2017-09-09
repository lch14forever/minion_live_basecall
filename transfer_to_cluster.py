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

def transfer_file(source_file, cluster_cfg):
    source_basename = os.path.basename(source_file)
    host = cluster_cfg['host']
    port = 22
    transport = paramiko.Transport((host, port))
    transport.connect(username=cluster_cfg['user'], password=cluster_cfg['password'])
    sftp = paramiko.SFTPClient.from_transport(transport)
    target_folder = cluster_cfg['data_path']
    target_folder +=  '/' + cluster_cfg['libid'] + '/'   ## cluster path spec -- assuming linux
    try:
        tmp=sftp.stat(target_folder) ## Initially the folder need to be created
    except IOError:
        sftp.mkdir(target_folder)
    target_file = target_folder + source_basename
    sftp.put(source_file, target_file)
    sftp.close()
    transport.close()
    # ##TODO: I want something compatible for windows as well
    # target_file = cluster_cfg['data_path']
    # target_file +=  '/' + cluster_cfg['libid'] + '/'   ## cluster path spec -- assuming linux
    # login = ''.join([cluster_cfg['user'],"@", cluster_cfg['host'], ":"])
    # os.environ["RSYNC_PASSWORD"] = cluster_cfg['password']
    # cmd = ' '.join(['rsync -az --remove-source-files', source_file ,  login + target_file]) ## list does not work?
    # tmp = subprocess.check_output(cmd, shell=True)
    return target_file + '/' + source_basename

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
        ##sys.stderr.write("Using test MongoDB server\n")
        constr = mongo_conns['test']
    else:
        ##sys.stderr.write("Using production MongoDB server\n")
        constr = mongo_conns['production']
    try:
        connection = pymongo.MongoClient(constr)
    except pymongo.errors.ConnectionFailure:
        sys.stderr.write("Could not connect to the MongoDB server\n")
        return None
    ##sys.stderr.write("Database connection established\n")
    return connection
        
def make_tarfile(source_dir):
    """
    create a tar file from a directory
    """
    target_name = source_dir.rstrip(os.sep) + '.tar.gz'
    with tarfile.open(target_name, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    hasher = hashlib.sha1()
    with open(target_name, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return [target_name, hasher.hexdigest()]

def get_minion_param(source_dir):
    """
    get sequencing information libid, kit, flowcell
    """
    lib_path = os.path.split(os.path.dirname(source_dir.rstrip(os.sep)))
    assert(lib_path[-1]=='fast5') ## minknow default structure
    date, time, libid, flowcell, kit = lib_path[-2].split('_')
    return [libid, flowcell, kit]

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__)    
    parser.add_argument('inFolder', help="Input folder (A folder containing fast5 files)")
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
    compressed_file, tar_sha1 = make_tarfile(source_dir)
    libid, flowcell, kit = get_minion_param(compressed_file)
    ##2. rsync to server
    cluster_cfg['libid'] = libid 
    cluster_tar_path = transfer_file(compressed_file, cluster_cfg)
    epoch_present = int(time.time())*1000
    ##3. register into MangoDB
    conn = mongodb_conn(True)
           
    record = {
        'tar'       :   cluster_tar_path,
        'conda'     :   cluster_cfg['conda_path'],
        'env'       :   cluster_cfg['conda_env'],
        'sha1'      :   tar_sha1,
        'src'       :   cluster_cfg["process_src"],
        'kit'       :   kit,
        'flowcell'  :   flowcell,
        'status'    :   'unprocessed',
        'outsuffix' :   libid,### what should this be?
        'timestamp' :   epoch_present
    }
    tmp = insert_muxjob(conn, libid, record)

    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
