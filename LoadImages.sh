#!/bin/bash

set -- $(<karenin.var)

Ij=${10}
lsm2nrrd=${20}
inbox=${2}
proc=${3}

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
		