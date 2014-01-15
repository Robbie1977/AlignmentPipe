#!/bin/bash

set -- $(<./AlignmentPipe/settings.var)

Ij=${10}
lsm2nrrd=${20}
inbox=${2}
proc=${3}
ppro=${21}
chn=${30}
log=${4}

for f in $inbox*.{lsm,tif}
do
	echo Processing $f
	nice xvfb-run ${Ij} -macro ${lsm2nrrd} ${f} -batch
	inl=`echo $inbox | wc -c`
	fr=`echo $f | rev | cut -c 5- |rev | cut -c $inl-`
	
	if [ -e ${fr}_Fu*${chn}.nrrd ]
	then
		echo Successfully converted $f to `ls $fr*.nrrd | wc -l` NRRD files
		echo 'PreProccessing image channels:'
		python $ppro ${fr}_Fo-PP_C1.nrrd ${fr}_Fo-PP_C2.nrrd C 10 
        if [ -e ${fr}_Fo*BG.nrrd ]		
        then
            echo 'Cleaning...'
		    rm $f
		    mv $fr*.nrrd $proc
            mv $fr*.log $log
		    echo 'Pushed for processing...'
        else
            echo Error preprocessing ${fr}_Fo!
        fi

        python $ppro ${fr}_Fz-PP_C1.nrrd ${fr}_Fz-PP_C2.nrrd C 10 
        if [ -e ${fr}_Fz*BG.nrrd ]		
        then
            echo 'Cleaning...'
            rm $f
            mv $fr*.nrrd $proc
            mv $fr*.log $log
            echo 'Pushed for processing...'
        else
            echo Error preprocessing ${fr}_Fz!
        fi

        python $ppro ${fr}_Fc-PP_C1.nrrd ${fr}_Fc-PP_C2.nrrd C 10 
        if [ -e ${fr}_Fc*BG.nrrd ]		
        then
            echo 'Cleaning...'
            rm $f
            mv $fr*.nrrd $proc
            mv $fr*.log $log
            echo 'Pushed for processing...'
        else
            echo Error preprocessing ${fr}_Fc!
        fi

        python $ppro ${fr}_Fu-PP_C1.nrrd ${fr}_Fu-PP_C2.nrrd C 10 
        if [ -e ${fr}_Fu*BG.nrrd ]		
        then
            echo 'Cleaning...'
            rm $f
            mv $fr*.nrrd $proc
            mv $fr*.log $log
            echo 'Pushed for processing...'
        else
            echo Error preprocessing ${fr}_Fu!
        fi

        
	else
		echo Error converting $f into NRRD files!
	fi
done		
		
