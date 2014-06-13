from pymongo import MongoClient
import os, sys, nrrd, cmtk
import numpy as np
import bson
import warpScoring.CheckImages as ci
from cmtk import collection, tempfolder, active, run_stage, cmtkdir, template, checkDir, host

def affineRec(record):
  record = checkDir(record)
  print 'Staring affine alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  affine, r = cmtk.affine(bgfile)
  print affine
  record['alignment_stage'] = 4
  if r > 0: record['alignment_stage'] = 0
  return record

def affine(name):
  for record in collection.find({'alignment_stage': 3, 'name': name}):
    collection.save(affineRec(record))

if __name__ == "__main__":
  if active and '3' in run_stage:
    total = collection.find({'alignment_stage': 3}).count()
    count = 0
    for record in collection.find({'alignment_stage': 3}):
      count +=1
      print 'Processing: ' + str(count) + ' of ' + str(total)
      collection.save(affineRec(record))
    print 'done'
  else:
    print 'inactive or stage 3 not selected'
