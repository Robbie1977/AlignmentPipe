#!/bin/bash

Ij='/disk/data/VFBTools/Fiji/ImageJ-linux64'
lsm2nrrd='/disk/data/VFBTools/lsm2nrrd/lsm2nrrd.ijm'
inbox='./inbox/*.lsm'
proc='./processing/'

for f in $inbox
do
	echo 'Processing $f'
	$Ij -macro $lsm2nrrd $f -batch
	fr=`echo $f | rev | cut -c 4- |rev`
	if [ -e $fr*C3.nrrd ] #note last channel number! 
	then
		echo Successfully converted $f to `ls $fr*.nrrd | wc -l` NRRD files
		echo 'Cleaning...'
		rm $f
		mv $fr*.nrrd $processing
		echo 'Pushed for processing...'
	fi
done		
		