#!/bin/bash

set -- $(<./AlignmentPipe/settings.var)

proc=${3}
logdir=${4}
outdir=${9}
cmtkdir=${11}
py=${12}
om=${22}
cm=${23}
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
            echo 'NOTE: there should be multiple warning messages reported as the files should not contain orientation meta data'
            echo Initial aligment:
            if [[ $fr == *_F?-PP* ]]
            then
                fr=`echo ${fr/_F?-PP/_Fo-PP}`
                if [ -e ${proc}${fr}.nrrd ]
                then
                    mv ${proc}${fr}.nrrd ${proc}${fr}${host}.nrrd
                fi
                
                fr=`echo ${fr/_F?-PP/_Fz-PP}`
                if [ -e ${proc}${fr}.nrrd ]
                then
                    mv ${proc}${fr}.nrrd ${proc}${fr}${host}.nrrd
                fi
                
                fr=`echo ${fr/_F?-PP/_Fc-PP}`
                if [ -e ${proc}${fr}.nrrd ]
                then
                    mv ${proc}${fr}.nrrd ${proc}${fr}${host}.nrrd
                fi
                
                fr=`echo ${fr/_F?-PP/_Fu-PP}`
                if [ -e ${proc}${fr}.nrrd ]
                then
                    mv ${proc}${fr}.nrrd ${proc}${fr}${host}.nrrd
                fi
                
                echo 'Finding the best orientation...'
                
                fr=`echo ${fr/_F?-PP/_Fo-PP}`
                if [ -e ${proc}${fr}${host}.nrrd ]    
                then
                    if [ ! -e ${proc}${fr}-initial.nrrd ]
                    then
                        echo 'Test aligning' $fr'...'
                        nice ${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${proc}${fr}${host}.nrrd ${proc}${fr}-initial.xform
                        nice ${cmtkdir}reformatx -o ${proc}${fr}-initial.nrrd --floating ${proc}${fr}${host}.nrrd ${Tfile} ${proc}${fr}-initial.xform
                    else
                        echo 'initial alignment for Fo already exists'
            	    fi
                    o=$(nice $py $om ${proc}${fr}-initial.nrrd ${Tfile} Q)
                else
                    o=-1
                    echo 'Error isolating' $fr 
                    ok=false
                fi
                
                fr=`echo ${fr/_F?-PP/_Fz-PP}`
                if [ -e ${proc}${fr}${host}.nrrd ]    
                then
                    if [ ! -e ${proc}${fr}-initial.nrrd ]
                    then
                        echo 'Test aligning' $fr'...'
                        nice ${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${proc}${fr}${host}.nrrd ${proc}${fr}-initial.xform
                        nice ${cmtkdir}reformatx -o ${proc}${fr}-initial.nrrd --floating ${proc}${fr}${host}.nrrd ${Tfile} ${proc}${fr}-initial.xform
                    else
                        echo 'initial alignment for Fz already exists'
                    fi
                    z=$(nice $py $om ${proc}${fr}-initial.nrrd ${Tfile} Q)
                else
                    z=-1
                    echo 'Error isolating' $fr 
                    ok=false
                fi
                                
                fr=`echo ${fr/_F?-PP/_Fc-PP}`
                if [ -e ${proc}${fr}${host}.nrrd ]    
                then
                    if [ ! -e ${proc}${fr}-initial.nrrd ]
                    then
                        echo 'Test aligning' $fr'...'
                        nice ${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${proc}${fr}${host}.nrrd ${proc}${fr}-initial.xform
                        nice ${cmtkdir}reformatx -o ${proc}${fr}-initial.nrrd --floating ${proc}${fr}${host}.nrrd ${Tfile} ${proc}${fr}-initial.xform
                    else
                        echo 'initial alignment for Fc already exists'
                    fi
                    c=$(nice $py $om ${proc}${fr}-initial.nrrd ${Tfile} Q)
                else
                    c=-1
                    echo 'Error isolating' $fr 
                    ok=false
                fi

                fr=`echo ${fr/_F?-PP/_Fu-PP}`
                if [ -e ${proc}${fr}${host}.nrrd ]    
                then
                    if [ ! -e ${proc}${fr}-initial.nrrd ]
                    then
                        echo 'Test aligning' $fr'...'
                        nice ${cmtkdir}make_initial_affine --principal-axes ${Tfile} ${proc}${fr}${host}.nrrd ${proc}${fr}-initial.xform
                        nice ${cmtkdir}reformatx -o ${proc}${fr}-initial.nrrd --floating ${proc}${fr}${host}.nrrd ${Tfile} ${proc}${fr}-initial.xform
                    else
                        echo 'initial alignment for Fu already exists'
                    fi
                    u=$(nice $py $om ${proc}${fr}-initial.nrrd ${Tfile} Q)
                else
                    u=-1
                    echo 'Error isolating' $fr 
                    ok=false
                fi

                echo 'Results:'$'\n'$o$'\n'$z$'\n'$c$'\n'$u

                if [ $(echo '('$o' > '$z') + ('$o' > '$c') + ('$o' > '$u')' | bc) == 3 ] 
                then
                    fr=`echo ${fr/_F?-PP/_Fo-PP}`
                fi

                if [ $(echo '('$z' > '$o') + ('$z' > '$c') + ('$z' > '$u')' | bc) == 3 ] 
                then
                    fr=`echo ${fr/_F?-PP/_Fz-PP}`
                fi

                if [ $(echo '('$c' > '$z') + ('$c' > '$o') + ('$c' > '$u')' | bc) == 3 ] 
                then
                    fr=`echo ${fr/_F?-PP/_Fc-PP}`
                fi

                if [ $(echo '('$u' > '$z') + ('$u' > '$c') + ('$u' > '$o')' | bc) == 3 ] 
                then
                    fr=`echo ${fr/_F?-PP/_Fu-PP}`
                fi
                
                echo $fr' chosen'
                                                                    
            fi    
            
            if [ -e ${proc}${fr}-initial.xform ]
            then
                echo Affine alignment:
                if [ ! -e ${proc}${fr}-affine.xform ]
                then
                    nice ${cmtkdir}registration --initial ${proc}${fr}-initial.xform --dofs 6,9 --auto-multi-levels 4 -o ${proc}${fr}-affine.xform ${Tfile} ${proc}${fr}${host}.nrrd
                else
                    echo affine alignment already exists
                fi
                if [ -e ${proc}${fr}-affine.xform ]
                then
                    echo 'Calulating final warp alignment: (This will take a long time...)'
                    if [ ! -e ${proc}${fr}-warp.xform ]
                    then
                        nice ${cmtkdir}warp -o ${proc}${fr}-warp.xform --grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1 --initial ${proc}${fr}-affine.xform ${Tfile} ${proc}${fr}${host}.nrrd
                    else
                        echo 'complete warp alignment already exists'
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
                            echo checking quality of alignment:
                            nice $py $om ${proc}${fr}${host}-aligned.nrrd ${Tfile} ${logdir}Quality.csv
                            nice $py $cm ${proc}${fr}${host}-aligned.nrrd ${Tfile} ${logdir}Quality.csv 
                            echo tidying up...
                            mv ${proc}${fm}*-aligned.nrrd ${outdir}
                            echo compressing:
                            tar -cvzf ${logdir}${fm}warp.tar ${proc}${fr}-warp.xform ${proc}${fm}*.nrrd --remove-files
                            rm -R ${proc}${fm}*
                            rm ${proc}${fr/_F?-PP/"_F?-PP"}*
                            mv ${outdir}${fr}${host}-aligned.nrrd ${outdir}${fr}-aligned.nrrd 
                            if [ -e ${proc}${fm}* ]
                            then
                                echo 'cleaning error: files remain in processing directory!'
                            else
                                echo 'Aligned files are in the output directory; compressed transforms and original converted files are stored in the log directory if required.'
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
    if [ -e ${proc}${fr/_F?-PP/_Fo-PP}${host}.nrrd ]
    then
        mv ${proc}${fr/_F?-PP/_Fo-PP}${host}.nrrd ${proc}${fr/_F?-PP/_Fo-PP}.nrrd
    fi
    if [ -e ${proc}${fr/_F?-PP/_Fz-PP}${host}.nrrd ]
    then
        mv ${proc}${fr/_F?-PP/_Fz-PP}${host}.nrrd ${proc}${fr/_F?-PP/_Fz-PP}.nrrd
    fi
    if [ -e ${proc}${fr/_F?-PP/_Fc-PP}${host}.nrrd ]
    then
        mv ${proc}${fr/_F?-PP/_Fc-PP}${host}.nrrd ${proc}${fr/_F?-PP/_Fc-PP}.nrrd
    fi
    if [ -e ${proc}${fr/_F?-PP/_Fu-PP}${host}.nrrd ]
    then
        mv ${proc}${fr/_F?-PP/_Fu-PP}${host}.nrrd ${proc}${fr/_F?-PP/_Fu-PP}.nrrd
    fi
    echo finished working with ${fm}*
done		
	
