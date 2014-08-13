import os, sys, nrrd, cmtk, gc
import numpy as np
import warpScoring.slicescore as slicescore
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir
from NRRDtools.labelObjects import labelObj, cutObj, cropObj


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
      cur.execute("UPDATE images_mask_original SET complete=True, cut_complete=False, crop_complete=False, detected_objects=%s WHERE id = %s ", [objs.tolist(), str(line[0])])
      cur.connection.commit()
      gc.collect()
    print 'done'
  else:
    print 'inactive or stage 0 not selected'

  if active and '0' in run_stage:
    cur.execute("SELECT images_mask_original.id, images_mask_original.cut_objects, images_original_nrrd.file, images_mask_original.auto_restart_alignment, images_alignment.id FROM images_mask_original, images_original_nrrd, images_alignment WHERE images_original_nrrd.id = images_mask_original.image_id AND images_original_nrrd.image_id = images_alignment.id AND images_mask_original.complete = True AND images_mask_original.cut_complete = False AND images_mask_original.cut_objects is not null AND images_mask_original.cut_objects != '' AND images_mask_original.cut_objects != '{}'")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Cut object(s) from original image: ' + str(count) + ' of ' + str(total)
      maskfile = str(line[2]).replace('.nrrd','-objMask.nrrd')
      cutObj(tempfolder + str(line[2]), tempfolder + maskfile, labels=str(line[1]))
      cur.execute("UPDATE images_mask_original SET cut_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
      if line[3]:
        print 'Auto restarting alignment...'
        cur.execute("UPDATE images_alignment SET alignment_stage=2 WHERE id = %s ", [str(line[4])])
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
      cur.execute("UPDATE images_mask_aligned SET complete=True, cut_complete=False, crop_complete=False, detected_objects=%s WHERE id = %s ", [objs.tolist(), str(line[0])])
      cur.connection.commit()
      gc.collect()
    print 'done'
  else:
    print 'inactive or stage 7 not selected'

  if active and '7' in run_stage:
    cur.execute("SELECT images_mask_aligned.id, images_mask_aligned.cut_objects, images_mask_aligned.channel, images_alignment.aligned_bg, images_alignment.aligned_sg, images_alignment.aligned_ac1, images_alignment.id FROM images_mask_aligned, images_alignment WHERE images_alignment.id = images_mask_aligned.image_id AND images_mask_aligned.complete = True AND images_mask_aligned.cut_complete = False AND images_mask_aligned.cut_objects is not null AND images_mask_aligned.cut_objects != '' AND images_mask_aligned.cut_objects != '{}'")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      chan = 4
      print 'Cut object(s) from original image: ' + str(count) + ' of ' + str(total)
      if str(line[2]) == 'bg':
        chan = 3
      if str(line[2]) == 'ac1':
        chan = 5
      maskfile = str(line[chan]).replace('.nrrd','-objMask.nrrd')
      cutObj(tempfolder + str(line[chan]), tempfolder + maskfile, labels=str(line[1]))
      cur.execute("UPDATE images_mask_aligned SET cut_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
    print 'done'
  else:
    print 'inactive or stage 0 not selected'
