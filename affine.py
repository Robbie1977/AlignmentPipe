import os, sys, nrrd, cmtk
import numpy as np
import bson
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir

def affineRec(record, template=template, bgfile='image_Ch1.nrrd', affineSet='--dofs 6,9 --auto-multi-levels 4'):
  record = checkDir(record)
  print 'Staring affine alignment for: ' + record['name']
  # bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  affine, r = cmtk.affine(bgfile, template=template, scale=affineSet)
  print affine
  record['alignment_stage'] = 4
  if r > 0: record['alignment_stage'] = 0
  record['max_stage'] = 4
  return record

def affine(name, template=template, bgfile='image_Ch1.nrrd', affineSet='--dofs 6,9 --auto-multi-levels 4'):
  cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 3 AND name like %s", [name])
  records = cur.fetchall()
  key = []
  for desc in cur.description:
      key.append(desc[0])
  for line in records:
      record = dict(zip(key,line))
      record = affineRec(record, template, bgfile, affineSet)
      u = ''
      for k, v in record.items():
        if not (k == 'id' or v == None or v == 'None'):
          if not u == '':
            u = u + ', '
          if type(v) == type(''):
            u = u + str(k) + " = '" + str(v) + "'"
          else:
            u = u + str(k) + " = " + str(v)
      print u
      cur.execute("UPDATE images_alignment SET " + u + " WHERE id = %s ", [str(record['id'])])
      cur.connection.commit()
  # for record in collection.find({'alignment_stage': 3, 'name': name}):
  # collection.save(affineRec(record))

if __name__ == "__main__":
  if active and '3' in run_stage:
    cur.execute("SELECT images_alignment.name, system_template.file, images_original_nrrd.file, system_setting.cmtk_affine_var FROM images_alignment, system_template, system_setting, images_original_nrrd WHERE alignment_stage = 3 AND images_original_nrrd.channel = images_alignment.background_channel AND images_original_nrrd.image_id = images_alignment.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Affine alignment: ' + str(count) + ' of ' + str(total)
      affine(line[0], template=(templatedir + line[1]), bgfile=(tempfolder + line[2]), affineSet=line[3])
    print 'done'
  else:
    print 'inactive or stage 3 not selected'

  # if active and '3' in run_stage:
  #   total = collection.find({'alignment_stage': 3}).count()
  #   count = 0
  #   for record in collection.find({'alignment_stage': 3}):
  #     count +=1
  #     print 'Processing: ' + str(count) + ' of ' + str(total)
  #     collection.save(affineRec(record))
  #   print 'done'
  # else:
  #   print 'inactive or stage 3 not selected'
