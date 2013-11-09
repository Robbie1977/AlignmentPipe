#!/bin/bash

set -- $(<./AlignmentPipe/settings.var)

Ij=${10}
lsm2nrrd=${20}
inbox=${2}
proc=${3}
ppro=${21}
chn=${30}
log=${4}

for f in $inbox*.lsm
do
	echo Processing $f
	nice xvfb-run ${Ij} -macro ${lsm2nrrd} ${f} -batch
	inl=`echo $inbox | wc -c`
	fr=`echo $f | rev | cut -c 5- |rev | cut -c $inl-`
	
	if [ -e $fr*$chn.nrrd ] 
	then
		echo Successfully converted $f to `ls $fr*.nrrd | wc -l` NRRD files
		echo 'PreProccessing image channels:'
		python $ppro $fr-PP_C1.nrrd $fr-PP_C2.nrrd ZC 10 
        if [ -e $fr*BG.nrrd ]		
        then
            echo 'Cleaning...'
		    rm $f
		    mv $fr*.nrrd $proc
            mv $fr*.log $log
		    echo 'Pushed for processing...'
        else
            echo Error preprocessing $fr!
        fi
	else
		echo Error converting $f into NRRD files!
	fi
done		
		
