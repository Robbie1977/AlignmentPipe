#!/bin/bash

set -- $(<./AlignmentPipe/settings.var)

proc=${3}
logdir=${4}
outdir=${9}
passdir=${13}
cmtkdir=${11}
py=${12}
om=${22}
cm=${23}
Tfile=${29}
host=-${HOSTNAME//./_}

for f in $outdir*BG.nrrd
do
    score=$(nice $py $om ${f} ${Tfile} Q)
    if [ score > 60 ]
    then
        fa=`echo ${f/PP_BG/"PP_?G"}`
        mv ${fa} ${passdir}
        echo ${fa} passed with a score of ${score}  
    else
        echo ${f} failed with a score of ${score} 
    fi
    
done     
