from pymongo import MongoClient
import os, sys, nrrd, cmtk
from tiffile import TiffFile
import numpy as np
import bson
import warpScoring.slicescore as slicescore
import warpScoring.CheckImages as ci
from cmtk import collection, tempfolder, active, run_stage, cmtkdir, template, threshold

def alignRec(record):
  print 'Finalising alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  record['aligned_BG']=cmtk.align(bgfile)
  record['aligned_avgSlice_score'] = str(ci.rateOne(record['aligned_BG'] ,results=None, methord=slicescore.avgOverlapCoeff))
  record['aligned_slice_score'] = str(ci.rateOne(record['aligned_BG'] ,results=None, methord=slicescore.OverlapCoeff))
  record['aligned_score'] = str(np.mean([np.float128(record['aligned_avgSlice_score']), np.float128(record['aligned_slice_score'])]))
  #Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
  print 'Result: ' + record['aligned_score']
  if record['aligned_score'] > threshold:
    record['alignment_stage'] = 6
    print 'Passed!'
  else:
    record['alignment_stage'] = 0
    print 'Failed!'
  return record

def alignRem(record):
  print 'Aligning signal, etc. for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  sgfile = record['original_nrrd'][('Ch' + str(record['signal_channel']) + '_file')]
  a=0
  for i in range(1,6):
    if not i == record['background_channel']:
      if i == record['signal_channel']:
        record['aligned_SG']=cmtk.align(sgfile, xform=bgfile.replace('.nrrd','_warp.xform'))
      else:
        if ('Ch' + str(i) + '_file') in record['original_nrrd'].keys():
          chfile = record['original_nrrd'][('Ch' + str(i) + '_file')]
          if os.path.isfile(chfile):
            a +=1
            record['aligned_AC'+str(a)]=cmtk.align(chfile, xform=bgfile.replace('.nrrd','_warp.xform'))
            record['AC'+str(a)+'_channel']=i
  record['alignment_stage'] = 7
  return record

def align(name):
  for record in collection.find({'alignment_stage': 5, 'name': name}):
    collection.save(alignRec(record))
  for record in collection.find({'alignment_stage': 6, 'name': name}):
    collection.save(alignRem(record))

if __name__ == "__main__":
  if active and '5' in run_stage:
    total = collection.find({'alignment_stage': 5}).count()
    count = 0
    for record in collection.find({'alignment_stage': 5}):
      count +=1
      print 'Processing: ' + str(count) + ' of ' + str(total)
      collection.save(alignRec(record))
    total = collection.find({'alignment_stage': 6}).count()
    count = 0
  else:
    print 'inactive or stage 5 not selected'
  if active and '6' in run_stage:
    for record in collection.find({'alignment_stage': 6}):
      count +=1
      print 'Processing: ' + str(count) + ' of ' + str(total)
      collection.save(alignRem(record))
    print 'done'
  else:
    print 'inactive or stage 6 not selected'
