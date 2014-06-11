#!/bin/bash

#run on servers 'nohup nice ./alignment_demon.sh &' and use web interface to control.

while true
do
  nice python convert.py
  nice python initial.py
  nice python affine.py
  nice python warp.py
  nice python align.py
done
