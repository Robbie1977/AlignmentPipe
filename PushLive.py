import os, sys, nrrd, cmtk, gc, subprocess
import numpy as np
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir

wlzDir = "/partition/bocian/VFBTools/Woolz2013Full/bin/"
Fiji = "/partition/bocian/VFBTools/Fiji/ImageJ-linux64"

def pushLive(id, name, sgfile):
    if (id > 999):
        first = str(id)[:-3]
        last = str(id)[-3:]
    else:
        first = "00"
        last = str(id)
    while len(first) < 2:
        first = "0" + first
    while len(last) < 3:
        last = "0" + last
    first = "A" + first
    os.symlink(sgfile, tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")

    print 'Linking ' + sgfile + ' to ' + "/data/VFB/i/" + first + "/" + last + "/volume.nrrd"
    subprocess.call("nice " + Fiji + " -macro nrrd2tif.ijm " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd" + " -batch", shell=True)
    # TBD: resolve voxel size from template.
    subprocess.call("nice " + wlzDir + "WlzExtFFConvert -f tif -F wlz " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.tif |" + wlzDir + "WlzThreshold -v2 |" + wlzDir + "WlzSetVoxelSize -z0.46 -x0.4612588 -y0.4612588 >" + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.wlz" , shell=True)
    print "Created wlz: " + "/VFB/i/" + first + "/" + last + "/volume.wlz"

if __name__ == "__main__":
  if active and '4' in run_stage:
    cur.execute("SELECT images_alignment.id, images_alignment.name, images_alignment.aligned_sg FROM images_alignment WHERE alignment_stage = 5 ORDER BY images_alignment.id")
    records = cur.fetchall()
    for line in records:
      pushLive(line[0], line[1], sgfile=(tempfolder + line[2])
    print 'done'
  else:
    print 'inactive or stage 4 not selected'
