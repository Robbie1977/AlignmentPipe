#!/bin/bash

set -- $(<./AlignmentPipe/settings.var)

proc=${3}
logdir=${4}
outdir=${9}
cmtkdir=${11}
Tfile=${29}
host=-${HOSTNAME//./_}

for f in $proc*BG.nrrd
do
	inl=`echo $proc | wc -c`
    fr=`echo $f | rev | cut -c 6- |rev | cut -c $inl-`
    fm=`echo $f | rev | cut -c 8- |rev | cut -c $inl-`
    if [ -e $f ]
    then
        echo claiming $fr on ${HOSTNAME}...
        mv $f ${proc}${fr}${host}.nrrd
        if [ -e ${proc}${fr}${host}.nrrd ]
        then
            echo Processing $f
            ok=true
            echo 'NOTE: there should be two warning messages reported as the files should not contain orientation data'
            echo Initial aligment:
            if [ ! -e ${proc}${fr}-initial.xform ]
            then
        	    nice ${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${proc}${fr}${host}.nrrd ${proc}${fr}-initial.xform
        	fi
            if [ -e ${proc}${fr}-initial.xform ]
            then
                echo Affine alignment:
                if [ ! -e ${proc}${fr}-affine.xform ]
                then
                    nice ${cmtkdir}registration --initial ${proc}${fr}-initial.xform --dofs 6,9 --auto-multi-levels 4 -o ${proc}${fr}-affine.xform ${Tfile} ${proc}${fr}${host}.nrrd
                fi
                if [ -e ${proc}${fr}-affine.xform ]
                then
                    echo 'Calulating final warp alignment: (This will take a long time...)'
                    if [ ! -e ${proc}${fr}-warp.xform ]
                    then
                        nice ${cmtkdir}warp -o ${proc}${fr}-warp.xform --grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1 --initial ${proc}${fr}-affine.xform ${Tfile} ${proc}${fr}${host}.nrrd
                    fi
                    if [ -e ${proc}${fr}-warp.xform ]
                    then
                        for sf in ${proc}${fm}*.nrrd
                        do
                            sfr=`echo $sf | rev | cut -c 6- |rev | cut -c $inl-`
                            echo Aligning ${sfr}:
                            nice ${cmtkdir}reformatx -o ${proc}${sfr}-aligned.nrrd --floating ${sf} ${Tfile} ${proc}${fr}-warp.xform
                            if [ -e ${proc}${sfr}-aligned.nrrd ]
                            then
                                echo ${sfr} aligned OK.
                            else
                                echo error applying warp to ${sfr}
                                ok=false
                            fi
                        done
                        if $ok
                        then
                            echo Alignment completed sucessfully!
                            echo tidying up...
                            tar -cvzf ${logdir}${fm}-warp.tar ${proc}${fr}-warp.xform ${proc}${fm}*.nrrd --remove-files
                            mv ${proc}${fm}*-aligned.nrrd ${outdir}
                            rm -R ${proc}${fm}
                            if [ -e ${proc}${fm}* ]
                            then
                                echo cleaning error: files remain in processing directory!
                            else
                                echo Aligned files are in the output directory; compressed transforms and original converted files are stored in the log directory if required.
                                echo .
                            fi
                        else
                            echo 'error: warp did not apply to all channels correctly! (See above for details)'
                        fi
                    else
                        echo error producing final warp alignment for $fr
                    fi
                else
                    echo error producing affine alignment for $fr
                fi
            else
                echo error producing initial alignment for $fr
            fi
        else
            echo 'failed to claim file. (OK if claimed by another machine)'
        fi
    else
        echo 'file no longer available for processing. (OK if processed by another machine)'
    fi    
    if [ -e ${proc}${fr}${host}.nrrd ]
    then
        mv ${proc}${fr}${host}.nrrd $f
    fi
    echo 'finished working with ${fm}*.'
done		
	
