#!/bin/bash

## temporarily used for live basecall before rpg take over

input=$1

server=lich@ionode:/mnt/projects/lich/dream_challenge/
target=${server}/N057_SQK308_MIN107/fast5/

scp -r $input $target

