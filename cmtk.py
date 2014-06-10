import sys, subprocess
from pymongo import MongoClient
from socket import gethostname

client = MongoClient('localhost', 27017)
db = client.alignment
collection = db.images_alignment

adjust_thresh = 0.0035
setting_id=u'1'
record = db.system_server.find_one({'host_name': gethostname()})
if record:
  if 'active' in record:
    active = record['active']
  if 'use_settings_id' in record:
    setting_id = record['use_settings_id']
  if 'use_DB' in record:
    useDB = record['use_DB']
  if 'run_stages' in record:
    run_stage = str.split(str(record['run_stages']),',')

  record = db.system_setting.find_one({'_id': setting_id})
  if record:
    if 'temp_dir' in record:
      tempfolder = record['temp_dir']
    if 'cmtk_dir' in record:
      cmtkdir = record['cmtk_dir']
    if 'template' in record:
      template = record['template']
    if 'auto_balance_th' in record:
      adjust_thresh = float(record['auto_balance_th'])
    if 'initial_pass_level' in record:
      init_threshold = record['initial_pass_level']
    if 'final_pass_level' in record:
      threshold = record['final_pass_level']

  if not str(useDB) == 'localhost':
    client = MongoClient(str(useDB), 27017)
    db = client.alignment
    collection = db.processing


  floatingImage = 'default.nrrd'

  def initial(floatingImage, xformOUT=floatingImage.replace('.nrrd','_initial.xform'), template=template, mode='--principal-axes'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_initial.xform')
    print 'nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT)
    subprocess.call('nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT), shell=True)
    return xformOUT

  def affine(floatingImage, xformOUT=floatingImage.replace('.nrrd','_affine.xform'), xformIN=floatingImage.replace('.nrrd','_initial.xform'), template=template, scale='--dofs 6,9 --auto-multi-levels 4'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_affine.xform')
    if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_initial.xform')
    print 'nice %sregistration --initial %s %s -o %s %s %s' % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage)
    subprocess.call('nice %sregistration --initial %s %s -o %s %s %s' % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage), shell=True)
    return xformOUT

  def warp(floatingImage, xformOUT=floatingImage.replace('.nrrd','_warp.xform'), xformIN=floatingImage.replace('.nrrd','_affine.xform'), template=template, settings='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_warp.xform')
    if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_affine.xform')
    print 'nice %swarp -o %s %s --initial %s %s %s' % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage)
    subprocess.call('nice %swarp -o %s %s --initial %s %s %s' % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage), shell=True)
    return xformOUT

  def align(floatingImage, xform=floatingImage.replace('.nrrd','_warp.xform'), imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd'), template=template):
    if 'default' in xform: xform=floatingImage.replace('.nrrd','_warp.xform')
    if 'default' in imageOUT: imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd')
    print 'nice %sreformatx -o %s --floating %s %s %s' % (cmtkdir, imageOUT, floatingImage, template, xform)
    subprocess.call('nice %sreformatx -o %s --floating %s %s %s' % (cmtkdir, imageOUT, floatingImage, template, xform), shell=True)
    return imageOUT
else:
  print 'No active records found!'
