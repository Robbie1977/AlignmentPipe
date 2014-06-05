from pymongo import MongoClient
import os, sys, nrrd, cmtk
from tiffile import TiffFile
import numpy as np
import bson
import warpScoring.CheckImages as ci

client = MongoClient('localhost', 27017)
db = client.alignment
collection = db.processing

param = db.param.temp.find()
for record in param:
  if 'folder' in record:
    tempfolder = record['folder']
param = db.param.local.find()
for record in param:
  if 'cmtkDir' in record:
    cmtkdir = record['cmtkDir']
  # if 'python' in record:
  #   py = record['python']
  if 'TAG_template' in record:
    template = record['TAG_template']
  if 'final_pass_level' in record:
    threshold = record['final_pass_level']

def alignRec(record):
  print 'Finalising alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  record['aligned_BG']=cmtk.align(bgfile)
  record['aligned_score'] = str(ci.rateOne(record['aligned_BG'] ,results=None))
  #Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
  print 'Result: ' + record['aligned_score']
  if record['aligned_score'] > threshold:
    record['alignment_stage'] = 6
  else:
    record['alignment_stage'] = 0
  collection.save(record)

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
        if ('Ch' + str(i) + '_file') in rec['original_nrrd'].keys():
          chfile = record['original_nrrd'][('Ch' + str(i) + '_file')]
          if os.path.isfile(chfile):
            a +=1
            record['aligned_AC'+str(a)]=cmtk.align(sgfile, xform=bgfile.replace('.nrrd','_warp.xform'))
            record['AC'+str(a)+'_channel']=i
  record['alignment_stage'] = 7
  collection.save(record)

def align(name):
  for record in collection.find({'alignment_stage': 5, 'name': name}):
    alignRec(record)
  for record in collection.find({'alignment_stage': 6, 'name': name}):
    alignRem(record)

if __name__ == "__main__":
  for record in collection.find({'alignment_stage': 5}):
    alignRec(record)
  for record in collection.find({'alignment_stage': 6}):
    alignRec(record)
  print 'done'
