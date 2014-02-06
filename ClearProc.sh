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


for f in $proc*BG*uk.nrrd
do
    echo 'remaning ' $f ' to ' ${f/} ${f/_BG-*_inf.ed.ac.uk.nrrd/_BG.nrrd}
    mv $f ${f/} ${f/_BG-*_inf.ed.ac.uk.nrrd/_BG.nrrd} 
done