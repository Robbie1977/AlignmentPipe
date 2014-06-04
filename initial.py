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
  if 'initial_pass_level' in record:
    threshold = record['initial_pass_level']

def initialRec(record):
  print 'Staring initial alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  record['temp_initial_nrrd']=cmtk.align(bgfile, cmtk.initial(bgfile), imageOUT=tempfolder + record['name'] + '_initial.nrrd')
  record['temp_initial_score'] = str(ci.rateOne(record['temp_initial_nrrd'] ,results=None))
  #Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
  print 'Result: ' + record['temp_initial_score']
  if record['temp_initial_score'] > threshold:
    record['alignment_stage'] = 3
  else:
    record['alignment_stage'] = 0
  collection.save(record)

def initial(name):
  for record in collection.find({'alignment_stage': 2, 'name': name}):
    initialRec(record)

if __name__ == "__main__":
  for record in collection.find({'alignment_stage': 2}):
    initialRec(record)
  print 'done'
