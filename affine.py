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
  if 'TAG_template' in record:
    template = record['TAG_template']

def affineRec(record):
  print 'Staring affine alignment for: ' + record['name']
  bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
  print cmtk.affine(bgfile)
  record['alignment_stage'] = 4
  collection.save(record)

def affine(name):
  for record in collection.find({'alignment_stage': 3, 'name': name}):
    warpRec(record)
  
if __name__ == "__main__":
  for record in collection.find({'alignment_stage': 3}):
    warpRec(record)
  print 'done'
