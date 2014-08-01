import os, sys, nrrd, json
from tiffile import TiffFile, imsave
import numpy as np
from cmtk import tempfolder, active, run_stage, host, templatedir, cur, comp_orien, ori, orien


def createTiff(RedCh=None, GreenCh=None, BlueCh=None, Output='merged.tif'):
  if not RedCh == None:
    print 'Loading red channel: ' + str(RedCh)
    dataR, headerR = nrrd.read(str(RedCh))
    sh = np.shape(dataR)
    header = headerR
    print '...'
  if not GreenCh == None:
    print 'Loading green channel: ' + str(GreenCh)
    dataG, headerG = nrrd.read(str(GreenCh))
    sh = np.shape(dataG)
    header = headerG
    print '...'
  if not BlueCh == None:
    print 'Loading blue channel: ' + str(BlueCh)
    dataB, headerB = nrrd.read(str(BlueCh))
    sh = np.shape(dataB)
    header = headerB
    print '...'
  if RedCh == None:
    dataR = np.zeros(sh, dtype=np.uint8)
    headerR = header
  if GreenCh == None:
    dataG = np.zeros(sh, dtype=np.uint8)
    headerG = header
  if BlueCh == None:
    dataB = np.zeros(sh, dtype=np.uint8)
    headerB = header

  if not (np.shape(dataR) == np.shape(dataG) == np.shape(dataB)):
    print "Error: images not the same size!"
    return 0
  else:
    print 'Merging...'
    dataR = np.swapaxes(dataR,0,-1)
    dataR = np.expand_dims(dataR,axis=0)
    dataR = np.expand_dims(dataR,axis=2)
    dataG = np.swapaxes(dataG,0,-1)
    dataG = np.expand_dims(dataG,axis=0)
    dataG = np.expand_dims(dataG,axis=2)
    out = np.concatenate((dataR,dataG),axis=2)
    del dataR, dataG, headerR, headerG
    dataB = np.swapaxes(dataB,0,-1)
    dataB = np.expand_dims(dataB,axis=0)
    dataB = np.expand_dims(dataB,axis=2)
    out = np.concatenate((out,dataB),axis=2)
    del dataB, headerB
    print 'Saving merged tif file: ' + str(Output)
    imsave(str(Output), out)
    return 1

def mergeRec(record):
  red = None
  green = None
  blue = None
  try:
    blue = tempfolder + str(record['aligned_bg'])
    green = tempfolder + str(record['aligned_sg'])
    red = tempfolder + str(record['aligned_ac1'])
  finally:
    file = str(record['name']) + '_aligned.tif'
    out = tempfolder + file
    record['aligned_tif'] = file
  r = createTiff(RedCh=red, GreenCh=green, BlueCh=blue, Output=out)
  record['last_host'] = host
  record['alignment_stage'] = 20

def merge(name):
  cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 10 AND name like %s", [name])
  records = cur.fetchall()
  key = []
  for desc in cur.description:
      key.append(desc[0])
  for line in records:
      record = dict(zip(key,line))
      cur.execute("UPDATE images_alignment SET alignment_stage = 1010, last_host = %s WHERE id = %s ", [str(host), str(record['id'])])
      cur.connection.commit()
      r = mergeRec(record)
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

if __name__ == "__main__":
  if active and '10' in run_stage:
    cur.execute("SELECT name FROM images_alignment WHERE alignment_stage = 10")
    records = cur.fetchall()
    total = len(records)
    count = 0
    for line in records:
      count +=1
      print 'Converting: ' + str(count) + ' of ' + str(total)
      merge(line[0])
    print 'done'
  else:
    print 'inactive or stage 10 not selected'
