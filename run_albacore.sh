#!/bin/bash

source activate nanopore_py3

inFolder=$1

outPrefix=${2:-./}

inFolder_n=`basename $inFolder`
outFolder=${outPrefix}${inFolder_n}.basecalled

threads=8
flowcell=FLO-MIN107
kit=SQK-LSK308

## 1. base call
full_1dsq_basecaller.py -i $inFolder -t $threads -s $outFolder -f $flowcell -k $kit -n 0 -o fastq -q 1000000 ## both fastq and fasta produced

## 2. extract 1d reads
cat ${outFolder}/workspace/*fastq | gzip - >  ${outFolder}/1d.fastq.gz
cat ${outFolder}/1dsq_analysis/workspace/*fastq | gzip - >  ${outFolder}/1d2.fastq.gz

## 3. clean up
rm -rf ${outFolder}/workspace
rm -rf ${outFolder}/1dsq_analysis/workspace

## 4. tar everything
tar -czf ${outFolder}.tar.gz ${outFolder} --remove-files

source deactivate
## 5. remove input folder
rm -rf $inFolder
