import sys
from pymongo import MongoClient

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
    TAGtemplate = record['TAG_template']

def initial(floatingImage, xformOUT=tempfolder, template=TAGtemplate, mode='--principal-axes')
  subprocess.call('nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT), shell=True)
  return xformOUT

def affine(floatingImage, xformOUT=tempfolder, xformIN=tempfolder, template=TAGtemplate, mode='--principal-axes')
