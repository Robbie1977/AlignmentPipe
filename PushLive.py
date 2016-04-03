import os, sys, nrrd, cmtk, gc, subprocess, shutil, png
import numpy as np
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir
from PIL import Image

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
        shutil.copyfile(sgfile, tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")
        data, head = nrrd.read(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd")
        if head['sizes'][2] == 185:
            print "Inflating from " + str(head['sizes'][2]) + " slices to 270..."
            dataNew = np.zeros([head['sizes'][0],head['sizes'][1],270],dtype=np.uint8)
            dataNew[:,:,25:210]=data;
            head['encoding'] = 'gzip'
            if head.has_key('space direction'):
                head.pop("space directions", None)
            data = dataNew
        im = np.transpose(np.max(data,axis=2))
        if (data[0][0][0] < 1):
            data[0][0][0] = np.uint8(100)
        filesize = np.subtract(data.shape, 1)
        if (data[filesize[0]][filesize[1]][filesize[2]] < 1):
            data[filesize[0]][filesize[1]][filesize[2]] = np.uint8(100)
        nrrd.write(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd", data, options=head)
        print "Creating Thumbnail"
        im = Image.fromarray(im)
        if np.shape(im)[0] < np.shape(im)[1]:
            im = im.resize((120,60), Image.ANTIALIAS)
        elif np.shape(im)[0] > np.shape(im)[1]:
            im = im.resize((60,120), Image.ANTIALIAS)
        else:
            im = im.resize((60,60), Image.ANTIALIAS)
        im.save(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/thumbnail.png","PNG")
        print "Converting to Tiff"
        subprocess.call(Fiji + " -macro nrrd2tif.ijm " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.nrrd" + " -batch", shell=True)
        
        if os.path.isfile(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.wlz"):
            os.remove(tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.wlz")
            print "Clearing old woolz data..."
        
        print "Creating wlz: " + "/VFB/i/" + first + "/" + last + "/volume.wlz"
        print "Using voxel sizes: Z:" + head['space directions'][2][2] + ", X:" + head['space directions'][0][0] + ", Y:" + head['space directions'][1][1]
        
        subprocess.call("nice " + wlzDir + "WlzExtFFConvert -f tif -F wlz " + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.tif |" + wlzDir + "WlzThreshold -v50 |" + wlzDir + "WlzSetVoxelSize -z" + head['space directions'][2][2] + " -x" + head['space directions'][0][0] + " -y" + head['space directions'][1][1] + " >" + tempfolder + "../../IMAGE_DATA/VFB/i/" + first + "/" + last + "/volume.wlz" , shell=True)
        
        cur.execute("UPDATE images_alignment SET alignment_stage = 21, notes = %s WHERE id = %s", [str("VFB_"+first+last),str(id)])
        cur.connection.commit()
    else:
        print "Skipping " + name
    gc.collect()

if __name__ == "__main__":
  if active and '5' in run_stage:
    cur.execute("SELECT id, name, aligned_sg FROM images_alignment WHERE alignment_stage = 11 ORDER BY images_alignment.id")
    records = cur.fetchall()
    for line in records:
        try:
            pushLive(line[0], line[1], sgfile=(tempfolder + line[2]))
        except:
          cur.execute("UPDATE images_alignment SET alignment_stage = 21, notes = 'FAILED' WHERE id = %s", [str(line[0])])
          cur.connection.commit()
    print 'done'
  else:
    print 'inactive or stage 4 not selected'
