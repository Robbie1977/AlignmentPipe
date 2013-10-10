#!/bin/bash

set -- $(<settings.var)

proc=${3}
cmtk=${11}

for f in $proc*-PP_C3.nrrd
do
	echo 'Processing $f'
	echo 'Initial aligment:'
	$cmtk
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
	