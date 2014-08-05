import os, sys, nrrd, cmtk, gc
import numpy as np
import warpScoring.CheckImages as ci
from cmtk import cur, tempfolder, active, run_stage, cmtkdir, template, checkDir, host, templatedir

def warpRec(record, template=template, bgfile='image_Ch1.nrrd', warpSet='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
  record = checkDir(record)
  print 'Staring warping alignment for: ' + record['name']
  # bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  warp, r = cmtk.warp(bgfile, template=template, settings=warpSet)
  record['alignment_stage'] = 5
  if r > 0: record['alignment_stage'] = 0
  record['max_stage'] = 5
  record['last_host'] = host
  return record

def warp(name, template=template, bgfile='image_Ch1.nrrd', warpSet='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
  cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 4 AND name like %s", [name])
  records = cur.fetchall()
  key = []
  for desc in cur.description:
      key.append(desc[0])
  for line in records:
      record = dict(zip(key,line))
      # clear old failed alignments:
      cur.execute("UPDATE images_alignment SET alignment_stage = 4 WHERE last_host = %s AND alignment_stage = 1004", [str(host)])
      cur.connection.commit()
      # remove image from stack before processing:
      cur.execute("UPDATE images_alignment SET alignment_stage = 1004, last_host = %s WHERE id = %s ", [str(host), str(record['id'])])
      cur.connection.commit()
      record = warpRec(record, template, bgfile, warpSet)
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
      gc.collect()

if __name__ == "__main__":
  if active and '4' in run_stage:
    cur.execute("SELECT images_alignment.name, system_template.file, images_original_nrrd.file, system_setting.cmtk_warp_var FROM images_alignment, system_template, system_setting, images_original_nrrd WHERE alignment_stage = 4 AND images_original_nrrd.channel = images_alignment.background_channel AND images_original_nrrd.image_id = images_alignment.id AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Warp alignment: ' + str(count) + ' of ' + str(total)
      warp(line[0], template=(templatedir + line[1]), bgfile=(tempfolder + line[2]), warpSet=line[3])
    print 'done'
  else:
    print 'inactive or stage 4 not selected'
