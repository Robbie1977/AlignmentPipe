#!/bin/bash

set -- $(<settings.var)

Ij=${10}
lsm2nrrd=${20}
inbox=${2}
proc=${3}
ppro=${21}
chn=${30}

for f in $inbox*.lsm
do
	echo Processing $f
	xvfb-run $Ij -macro $lsm2nrrd $f -batch
	fr=`echo $f | rev | cut -c 4- |rev`
	if [ -e $fr*$chn.nrrd ] #note last channel number! 
	then
		echo Successfully converted $f to `ls $fr*.nrrd | wc -l` NRRD files
		echo 'PreProccessing image channels:'
		python $ppro $fr-PP_C1.nrrd $fr-PP_C2.nrrd C 10 
		echo 'Cleaning...'
		rm $f
		mv $fr*.nrrd $processing
		echo 'Pushed for processing...'
	else
		echo Error converting $f into NRRD files!
	fi
done		
		
