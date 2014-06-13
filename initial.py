from pymongo import MongoClient
import os, sys, nrrd, cmtk
import numpy as np
import bson
import warpScoring.CheckImages as ci
from cmtk import collection, tempfolder, active, run_stage, cmtkdir, template, init_threshold, checkDir, host

def initialRec(record):
  record = checkDir(record)
  print 'Staring initial alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  record['temp_initial_nrrd'], r =cmtk.align(bgfile, cmtk.initial(bgfile)[0], imageOUT=tempfolder + record['name'] + '_initial.nrrd')
  record['temp_initial_score'] = str(ci.rateOne(record['temp_initial_nrrd'] ,results=None))
  #Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
  print 'Result: ' + record['temp_initial_score']
  if record['temp_initial_score'] > init_threshold:
    record['alignment_stage'] = 3
  else:
    record['alignment_stage'] = 0
  if r > 0: record['alignment_stage'] = 0
  return record

def initial(name):
  for record in collection.find({'alignment_stage': 2, 'name': name}):
    collection.save(initialRec(record))

if __name__ == "__main__":
  if active and '2' in run_stage:
    total = collection.find({'alignment_stage': 2}).count()
    count = 0
    for record in collection.find({'alignment_stage': 2}):
      count +=1
      print 'Processing: ' + str(count) + ' of ' + str(total)
      collection.save(initialRec(record))
    print 'done'
  else:
    print 'inactive or stage 2 not selected'
