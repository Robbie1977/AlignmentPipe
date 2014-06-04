import sys, subprocess
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

floatingImage = 'default.nrrd'

def initial(floatingImage, xformOUT=floatingImage.replace('.nrrd','_initial.xform'), template=TAGtemplate, mode='--principal-axes'):
  if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_initial.xform')
  print 'nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT)
  subprocess.call('nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT), shell=True)
  return xformOUT

def affine(floatingImage, xformOUT=floatingImage.replace('.nrrd','_affine.xform'), xformIN=floatingImage.replace('.nrrd','_initial.xform'), template=TAGtemplate, scale='--dofs 6,9 --auto-multi-levels 4'):
  if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_affine.xform')
  if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_initial.xform')
  print 'nice %sregistration --initial %s %s -o %s %s %s' % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage)
  subprocess.call('nice %sregistration --initial %s %s -o %s %s %s' % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage), shell=True)
  return xformOUT

def warp(floatingImage, xformOUT=floatingImage.replace('.nrrd','_warp.xform'), xformIN=floatingImage.replace('.nrrd','_affine.xform'), template=TAGtemplate, settings='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
  if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_warp.xform')
  if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_affine.xform')
  print 'nice %swarp -o %s %s --initial %s %s %s' % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage)
  subprocess.call('nice %swarp -o %s %s --initial %s %s %s' % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage), shell=True)
  return xformOUT

def align(floatingImage, xform=floatingImage.replace('.nrrd','_warp.xform'), imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd'), template=TAGtemplate):
  if 'default' in xform: xform=floatingImage.replace('.nrrd','_warp.xform')
  if 'default' in imageOUT: imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd')
  print 'nice %sreformatx -o %s --floating %s %s %s' % (cmtkdir, imageOUT, floatingImage, template, xform)
  subprocess.call('nice %sreformatx -o %s --floating %s %s %s' % (cmtkdir, imageOUT, floatingImage, template, xform), shell=True)
  return imageOUT
