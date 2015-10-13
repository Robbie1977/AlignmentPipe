import os, sys, nrrd, cmtk, gc, stat, shutil
import numpy as np
import warpScoring.slicescore as slicescore
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir
from NRRDtools.labelObjects import labelObj, cutObj, cropObj


if __name__ == "__main__":
  if active and '0' in run_stage:
    cur.execute("SELECT images_mask_original.id, images_mask_original.intensity_threshold, images_mask_original.min_object_size, images_original_nrrd.file FROM images_mask_original, images_original_nrrd WHERE images_original_nrrd.id = images_mask_original.image_id AND images_mask_original.complete = False ORDER BY images_mask_original.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Create original image mask: ' + str(count) + ' of ' + str(total)
      outfile = str(line[3]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[3]).replace('.nrrd','-modFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[3]), tempfolder + modfile)
      objs = labelObj(tempfolder + str(line[3]), tempfolder + outfile, t=line[1], ms=line[2])
      cur.execute("UPDATE images_mask_original SET complete=True, cut_complete=False, crop_complete=False, detected_objects=%s WHERE id = %s ", [objs.tolist(), str(line[0])])
      cur.connection.commit()
      gc.collect()
      try:
        os.chmod(tempfolder + outfile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
      except:
        pass
    print 'done'
  else:
    print 'inactive or stage 0 not selected'

  if active and '0' in run_stage:
    cur.execute("SELECT images_mask_original.id, images_mask_original.cut_objects, images_original_nrrd.file, images_mask_original.auto_restart_alignment, images_alignment.id, images_original_nrrd.id, images_mask_original.overwrite_original, images_alignment.name FROM images_mask_original, images_original_nrrd, images_alignment WHERE images_original_nrrd.id = images_mask_original.image_id AND images_original_nrrd.image_id = images_alignment.id AND images_mask_original.complete = True AND images_mask_original.cut_complete = False AND images_mask_original.cut_objects is not null AND images_mask_original.cut_objects != '' AND images_mask_original.cut_objects != '{}' ORDER BY images_mask_original.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Cut object(s) from original image: ' + str(count) + ' of ' + str(total)
      maskfile = str(line[2]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[2]).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[2]),tempfolder + modfile)
      cutObj(tempfolder + modfile, tempfolder + maskfile, labels=str(line[1]))
      cur.execute("UPDATE images_mask_original SET cut_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
      newId = str(line[4])
      oldId = str(line[4])
      if line[6]:
          print 'Updating with results...'
          cur.execute("UPDATE images_original_nrrd SET file=%s WHERE id = %s ", [modfile, str(line[5])])
          cur.connection.commit()
          gc.collect()
      else:
        print 'Creating new alignment record with results...'
        print "Old ID: " + str(oldId)
        oldName = str(line[7])
        newName = str(line[7]) + "_ModByMask" + str(line[0])
        cur.execute("INSERT INTO images_alignment(name, settings_id, max_stage, last_host, alignment_stage, orig_orientation, loading_host, original_ext, original_path, crop_xyz, background_channel, signal_channel, ac1_channel, notes, reference, user_id) SELECT %s, settings_id, 2, last_host, alignment_stage, orig_orientation, loading_host, original_ext, original_path, crop_xyz, background_channel, signal_channel, ac1_channel, notes, reference, user_id FROM images_alignment WHERE id = %s", [newName, oldId])
        cur.connection.commit()
        gc.collect()
        cur.execute("SELECT id FROM images_alignment WHERE name = %s", [newName])
        results = cur.fetchall()
        newId = results[0][0]
        gc.collect()
        print "New ID: " + str(newId)
        cur.execute("INSERT INTO images_original_nrrd ( image_id, channel, new_min, new_max, file, is_index, pre_hist ) SELECT %s, channel, new_min, new_max, replace(file, %s, %s), is_index, pre_hist FROM images_original_nrrd WHERE image_id = %s", [newId, oldName, newName, oldId])
        cur.connection.commit()
        gc.collect()
        cur.execute("SELECT file, id FROM images_original_nrrd WHERE image_id = %s", [newId])
        results = cur.fetchall()
        print 'Duplicating files...'
        newOrig = line[5]
        for fl in results:
            shutil.copyfile(tempfolder + str(fl[0]).replace(newName, oldName),tempfolder + str(fl[0]))
            if (str(line[2]) == str(fl[0]).replace(newName, oldName)):
                newOrig = fl[1]
                print 'file matched'
        shutil.copyfile(tempfolder + modfile,tempfolder + str(line[2]).replace(oldName, newName))
        print 'Switching to new alignment via ' + str(newOrig)
        cur.execute("UPDATE images_mask_original SET image_id=%s WHERE id = %s ", [newOrig, line[0]])
        cur.connection.commit()
        gc.collect()
      if line[3]:
        print 'Auto restarting alignment...'
        cur.execute("UPDATE images_alignment SET alignment_stage=2002 WHERE id = %s ", [newId])
        cur.connection.commit()
        gc.collect()
        try:
          os.chmod((tempfolder + modfile), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except:
          pass

    print 'done'
  else:
    print 'inactive or stage 0 not selected'

  if active and '0' in run_stage:
    cur.execute("SELECT images_mask_original.id, images_mask_original.crop_objects, images_original_nrrd.file, images_mask_original.auto_restart_alignment, images_alignment.id, images_original_nrrd.id FROM images_mask_original, images_original_nrrd, images_alignment WHERE images_original_nrrd.id = images_mask_original.image_id AND images_original_nrrd.image_id = images_alignment.id AND images_mask_original.complete = True AND images_mask_original.crop_complete = False AND images_mask_original.crop_objects is not null AND images_mask_original.crop_objects != '' AND images_mask_original.crop_objects != '{}' ORDER BY images_mask_original.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Crop object(s) from original image: ' + str(count) + ' of ' + str(total)
      maskfile = str(line[2]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[2]).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[2]),tempfolder + modfile)
      cropObj(tempfolder + modfile, tempfolder + maskfile, labels=str(line[1]))
      cur.execute("UPDATE images_mask_original SET crop_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
      if line[3]:
        print 'Updating with results...'
        cur.execute("UPDATE images_original_nrrd SET file=%s WHERE id = %s ", [modfile, str(line[5])])
        cur.connection.commit()
        gc.collect()
        print 'Auto restarting alignment...'
        cur.execute("UPDATE images_alignment SET alignment_stage=2002 WHERE id = %s ", [str(line[4])])
        cur.connection.commit()
        gc.collect()
        try:
          os.chmod(tempfolder + str(line[2]), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except:
          pass
    print 'done'
  else:
    print 'inactive or stage 0 not selected'

  if active and '7' in run_stage:
    cur.execute("SELECT images_mask_aligned.id, images_mask_aligned.intensity_threshold, images_mask_aligned.min_object_size, images_mask_aligned.channel, images_alignment.aligned_bg, images_alignment.aligned_sg, images_alignment.aligned_ac1 FROM images_mask_aligned, images_alignment WHERE images_alignment.id = images_mask_aligned.image_id AND images_mask_aligned.complete = False ORDER BY images_mask_aligned.id")
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
      outfile = str(line[chan]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[chan]).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[chan]), tempfolder + modfile)
      objs = labelObj(tempfolder + str(line[chan]), tempfolder + outfile, t=line[1], ms=line[2])
      cur.execute("UPDATE images_mask_aligned SET complete=True, cut_complete=False, crop_complete=False, detected_objects=%s WHERE id = %s ", [objs.tolist(), str(line[0])])
      cur.connection.commit()
      gc.collect()
      try:
        os.chmod(tempfolder + outfile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
      except:
        pass
    print 'done'
  else:
    print 'inactive or stage 7 not selected'

  if active and '7' in run_stage:
    cur.execute("SELECT images_mask_aligned.id, images_mask_aligned.cut_objects, images_mask_aligned.channel, images_alignment.aligned_bg, images_alignment.aligned_sg, images_alignment.aligned_ac1, images_alignment.id FROM images_mask_aligned, images_alignment WHERE images_alignment.id = images_mask_aligned.image_id AND images_mask_aligned.complete = True AND images_mask_aligned.cut_complete = False AND images_mask_aligned.cut_objects is not null AND images_mask_aligned.cut_objects != '' AND images_mask_aligned.cut_objects != '{}' ORDER BY images_mask_aligned.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      chan = 4
      print 'Cut object(s) from aligned image: ' + str(count) + ' of ' + str(total)
      if str(line[2]) == 'bg':
        chan = 3
      if str(line[2]) == 'ac1':
        chan = 5
      maskfile = str(line[chan]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[chan]).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[chan]),tempfolder + modfile)
      cutObj(tempfolder + modfile, tempfolder + maskfile, labels=str(line[1]))
      print 'Updating with results...'
      cur.execute("UPDATE images_alignment SET images_alignment.aligned_%s=%s WHERE id = %s ", [str(line[2]), modfile, str(line[6])])
      cur.connection.commit()
      gc.collect()
      cur.execute("UPDATE images_mask_aligned SET cut_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
      try:
        os.chmod(tempfolder + str(line[chan]), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
      except:
        pass
    print 'done'
  else:
    print 'inactive or stage 7 not selected'

  if active and '7' in run_stage:
    cur.execute("SELECT images_mask_aligned.id, images_mask_aligned.crop_objects, images_mask_aligned.channel, images_alignment.aligned_bg, images_alignment.aligned_sg, images_alignment.aligned_ac1, images_alignment.id FROM images_mask_aligned, images_alignment WHERE images_alignment.id = images_mask_aligned.image_id AND images_mask_aligned.complete = True AND images_mask_aligned.crop_complete = False AND images_mask_aligned.crop_objects is not null AND images_mask_aligned.crop_objects != '' AND images_mask_aligned.crop_objects != '{}' ORDER BY images_mask_aligned.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      chan = 4
      print 'Crop to object(s) in aligned image: ' + str(count) + ' of ' + str(total)
      if str(line[2]) == 'bg':
        chan = 3
      if str(line[2]) == 'ac1':
        chan = 5
      maskfile = str(line[chan]).replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      modfile = str(line[chan]).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(line[0]) + '.nrrd')
      if not os.path.isfile(tempfolder + modfile):
          shutil.copyfile(tempfolder + str(line[chan]),tempfolder + modfile)
      cropObj(tempfolder + modfile, tempfolder + maskfile, labels=str(line[1]))
      print 'Updating with results...'
      cur.execute("UPDATE images_alignment SET images_alignment.aligned_%s=%s WHERE id = %s ", [str(line[2]), modfile, str(line[6])])
      cur.connection.commit()
      gc.collect()
      cur.execute("UPDATE images_mask_aligned SET crop_complete=True WHERE id = %s ", [str(line[0])])
      cur.connection.commit()
      gc.collect()
      try:
        os.chmod(tempfolder + str(line[chan]), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
      except:
        pass
    print 'done'
  else:
    print 'inactive or stage 7 not selected'
