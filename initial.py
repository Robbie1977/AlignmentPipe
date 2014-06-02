from pymongo import MongoClient
import os, sys, nrrd
from tiffile import TiffFile
import numpy as np
import bson

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
set -- $(<./AlignmentPipe/settings.var)

host=-${HOSTNAME//./_}

for record in collection.find({'temp_initial_nrrd': { '$exists': False } }):
  
