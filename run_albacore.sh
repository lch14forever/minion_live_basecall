#!/bin/bash

inFile=$1
outFolder=${2:-./}

inPrefix=${inFile%%.tar.gz}


## temp folder
tmp_folder=/dev/shm/tmp_albacore_`md5sum $inFile | cut -f1 -d' '`
##tmp_folder=./tmp_albacore_`md5sum $inFile | cut -f1 -d' '`
mkdir $tmp_folder

inFile_bs=`basename $inPrefix`
outFile=${outFolder}/${inFile_bs}.basecalled.tar.gz
tar -xf $inFile -C $tmp_folder --strip-components=1

## dirs for basecall
tmp_inFolder=${tmp_folder}/${inFile_bs}
tmp_outFolder=${tmp_folder}/${inFile_bs}.basecalled

## defaults:
threads=16
flowcell=FLO-MIN107
kit=SQK-LSK308


## 1. base call
source activate nanopore_py3
full_1dsq_basecaller.py -i $tmp_inFolder -t $threads -s $tmp_outFolder -f $flowcell -k $kit -n 0 -o fastq -q 1000000 ## both fastq and fasta produced

## 2. extract 1d reads
cat ${tmp_outFolder}/workspace/*fastq | gzip - >  ${tmp_outFolder}/1d.fastq.gz
cat ${tmp_outFolder}/1dsq_analysis/workspace/*fastq | gzip - >  ${tmp_outFolder}/1d2.fastq.gz

## 3. clean up
rm -rf ${tmp_outFolder}/workspace
rm -rf ${tmp_outFolder}/1dsq_analysis/workspace

## 4. tar everything

tar -czf $outFile -C ${tmp_outFolder} .

## 5. remove input folder
rm -rf $tmp_folder

#rm -f $inFile
