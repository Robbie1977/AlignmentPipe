#!/bin/bash

set -- $(<settings.var)

proc=${3}
cmtkdir=${11}
Tfile=${29}

for f in $proc*BG.nrrd
do
	echo 'Processing $f'
	echo 'Initial aligment:'
    inl=`echo $proc | wc -c`
    fr=`echo $f | rev | cut -c 6- |rev | cut -c $inl-`
	${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${fr}.nrrd
	fr=`echo $f | rev | cut -c 4- |rev`
	if [ -e $fr*C3.nrrd ] #note last channel number! 
	then
		echo Successfully converted $f to `ls $fr*.nrrd | wc -l` NRRD files
		echo 'Cleaning...'
		rm $f
		mv $fr*.nrrd $proc
		echo 'Pushed for processing...'
	fi
done		
	