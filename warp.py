from pymongo import MongoClient
import os, sys, nrrd, cmtk
import numpy as np
import bson
import warpScoring.CheckImages as ci
from cmtk import collection, tempfolder, active, run_stage, cmtkdir, template, checkDir, host

def warpRec(record):
  record = checkDir(record)
  print 'Staring warping alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  warp, r = cmtk.warp(bgfile)
  record['alignment_stage'] = 5
  if r > 0: record['alignment_stage'] = 0
  return record

def warp(name):
  for record in collection.find({'alignment_stage': 4, 'name': name}):
    collection.save(warpRec(record))

if __name__ == "__main__":
  if active and '4' in run_stage:
    total = collection.find({'alignment_stage': 4}).count()
    count = 0
    for record in collection.find({'alignment_stage': 4}):
      count +=1
      print 'Processing: ' + str(count) + ' of ' + str(total)
      collection.save(warpRec(record))
    print 'done'
  else:
    print 'inactive or stage 4 not selected'
