import os, sys, nrrd, cmtk
import numpy as np
import warpScoring.CheckImages as ci
from cmtk import tempfolder, active, run_stage, cmtkdir, checkDir, host, template, cur, templatedir



def initialRec(record, template=template, init_threshold=0.3, bgfile='image_Ch1.nrrd', alignSet='', initialSet='--principal-axes'):
  record = checkDir(record)
  print 'Staring initial alignment for: ' + record['name']
  # bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  record['temp_initial_nrrd'], r =cmtk.align(bgfile, cmtk.initial(bgfile, template=template, mode=initialSet)[0], imageOUT=tempfolder + record['name'] + '_initial.nrrd', template=template, settings=alignSet)
  record['temp_initial_score'] = str(ci.rateOne(record['temp_initial_nrrd'] ,results=None, template=template))
  #Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
  record['temp_initial_nrrd'] = str(record['temp_initial_nrrd']).replace(tempfolder,'')
  print 'Result: ' + record['temp_initial_score']
  if record['temp_initial_score'] > init_threshold:
    record['alignment_stage'] = 3
  else:
    record['alignment_stage'] = 0
  if r > 0: record['alignment_stage'] = 0
  record['max_stage'] = 3
  return record

def initial(name, template=template, init_threshold=0.3, bgfile='image_Ch1.nrrd', alignSet='', initialSet='--principal-axes'):
  cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 2 AND name like %s", [name])
  records = cur.fetchall()
  key = []
  for desc in cur.description:
      key.append(desc[0])
  for line in records:
      record = dict(zip(key,line))
      cur.execute("UPDATE images_alignment SET alignment_stage = 1002 WHERE id = %s ", [str(record['id'])])
      cur.connection.commit()
      record = initialRec(record, template, init_threshold, bgfile, alignSet, initialSet)
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
  # for record in collection.find({'alignment_stage': 2, 'name': name}):
  #   collection.save(initialRec(record))

if __name__ == "__main__":
  if active and '2' in run_stage:
    cur.execute("SELECT images_alignment.name, system_template.file, system_setting.initial_pass_level, images_original_nrrd.file, system_setting.cmtk_initial_var, system_setting.cmtk_align_var FROM images_alignment, system_template, system_setting, images_original_nrrd WHERE alignment_stage = 2 AND images_original_nrrd.channel = images_alignment.background_channel AND images_original_nrrd.image_id = images_alignment.id AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id")
    records = cur.fetchall()
    total = len(records)
    count = 0
    print records
    for line in records:
      count +=1
      print 'Initial alignment: ' + str(count) + ' of ' + str(total)
      initial(line[0], template=(templatedir + line[1]), init_threshold=line[2], bgfile=(tempfolder + line[3]), alignSet=line[5], initialSet=line[4])
    print 'done'
  else:
    print 'inactive or stage 2 not selected'

  # if active and '2' in run_stage:
  #   total = collection.find({'alignment_stage': 2}).count()
  #   count = 0
  #   for record in collection.find({'alignment_stage': 2}):
  #     count +=1
  #     print 'Processing: ' + str(count) + ' of ' + str(total)
  #     collection.save(initialRec(record))
  #   print 'done'
  # else:
  #   print 'inactive or stage 2 not selected'
