import os, sys, nrrd, cmtk, gc
import numpy as np
import warpScoring.slicescore as slicescore
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir
from NRRDtools.labelObjects import labelObj


if __name__ == "__main__":
  if active and '0' in run_stage:
    cur.execute("SELECT images_mask_original.id, images_mask_original.intensity_threshold, images_mask_original.min_object_size, images_original_nrrd.file FROM images_mask_original, images_original_nrrd WHERE images_original_nrrd.id = images_mask_original.image_id AND images_mask_original.complete = False")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Create original image mask: ' + str(count) + ' of ' + str(total)
      outfile = str(line[3]).replace('.nrrd','-objMask.nrrd')
      objs = labelObj(tempfolder + str(line[3]), tempfolder + outfile, t=line[1], ms=line[2])
      cur.execute("UPDATE images_mask_original SET complete=True, detected_objects=%s WHERE id = %s ", [str(objs), str(line[0])])
      cur.connection.commit()
      gc.collect()
    print 'done'
  else:
    print 'inactive or stage 0 not selected'

  if active and '7' in run_stage:
    cur.execute("SELECT images_mask_aligned.id, images_mask_aligned.intensity_threshold, images_mask_aligned.min_object_size, images_mask_aligned.channel, images_alignment.aligned_bg, images_alignment.aligned_sg, images_alignment.aligned_ac1 FROM images_mask_aligned, images_alignment WHERE images_alignment.id = images_mask_aligned.image_id AND images_mask_aligned.complete = False")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      chan = 5
      print 'Create aligned image mask: ' + str(count) + ' of ' + str(total)
      if str(line[3]) == 'bg':
        chan = 4
      if str(line[3]) == 'ac1':
        chan = 6
      outfile = str(line[chan]).replace('.nrrd','-objMask.nrrd')
      objs = labelObj(tempfolder + str(line[chan]), tempfolder + outfile, t=line[1], ms=line[2])
      cur.execute("UPDATE images_mask_aligned SET complete=True, detected_objects=%s WHERE id = %s ", [str(objs), str(line[0])])
      cur.connection.commit()
      gc.collect()
    print 'done'
  else:
    print 'inactive or stage 7 not selected'
