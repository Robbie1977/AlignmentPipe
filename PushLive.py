import os, sys, nrrd, cmtk, gc, subprocess
import numpy as np
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir

wlzDir = "/partition/bocian/VFBTools/Woolz2013Full/bin/"
Fiji = "nice /partition/bocian/VFBTools/Fiji/ImageJ-linux64 --headless"

def pushLive(id, name, sgfile):
    if os.path.exists(sgfile):
        if (id > 9999):
            first = str(id)[:-4]
            last = str(id)[-4:]
        else:
            first = "000"
            last = str(id)
        while len(first) < 3:
            first = "0" + first
        while len(last) < 4:
            last = "0" + last
        first = "a" + first
        if not os.path.exists(tempfolder + "../../IMAGE_DATA/VFB/i/" + first):
            os.makedirs(tempfolder + "../../IMAGE_DATA/VFB/i/" + first)
        if not os.path.exists(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last):
            os.makedirs(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last)
        print 'Linking ' + sgfile + ' to ' + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd"
        if os.path.exists(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd"):
            os.remove(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")
        os.symlink(sgfile, tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")
        data, head = nrrd.read(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")
        if head['sizes'][2] == 185:
            print "Inflating from " + str(head['sizes'][2]) + " slices to 270..."
            dataNew = np.zeros([head['sizes'][0],head['sizes'][1],270],dtype=np.uint8)
            dataNew[:,:,25:210]=data;
            head['encoding'] = 'gzip'
            if head['space directions'] == ['none', 'none', 'none']:
                head.pop("space directions", None)
            nrrd.write(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd", dataNew, options=head)
        print "Converting to Tiff"
        subprocess.call(Fiji + " -macro nrrd2tif.ijm " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd" + " -batch", shell=True)
        print "Creating wlz: " + "/VFB/i/" + first + "/" + last + "/volume.wlz"
        # TBD: resolve voxel size from template.
        subprocess.call("nice " + wlzDir + "WlzExtFFConvert -f tif -F wlz " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.tif |" + wlzDir + "WlzThreshold -v2 |" + wlzDir + "WlzSetVoxelSize -z0.46 -x0.4612588 -y0.4612588 >" + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.wlz" , shell=True)
        cur.execute("UPDATE images_alignment SET alignment_stage = 21 WHERE id = %s", [str(id)])
        cur.connection.commit()
    else:
        print "Skipping " + name
    gc.collect()

if __name__ == "__main__":
  if active and '5' in run_stage:
    cur.execute("SELECT id, name, aligned_sg FROM images_alignment WHERE alignment_stage = 11 ORDER BY images_alignment.id")
    records = cur.fetchall()
    for line in records:
      pushLive(line[0], line[1], sgfile=(tempfolder + line[2]))
    print 'done'
  else:
    print 'inactive or stage 4 not selected'
