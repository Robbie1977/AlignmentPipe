import sys, subprocess, os
from socket import gethostname
import psycopg2

con = psycopg2.connect(host='bocian.inf.ed.ac.uk', database='alignment', user='aligner_admin', password='default99')


ori = ['LPS','RPI','RAS','LAI','PLI','PRS','ALS','ARI'] #X(>),Y(\/),Z(X).
orien = [str(x).replace('R','right-').replace('L','left-').replace('P','posterior-').replace('A','anterior-').replace('S','superior').replace('I','inferior') for x in ori]
comp_orien = dict(zip(ori,orien))

cur = con.cursor()

adjust_thresh = 0.0035
setting_id=u'1'
host = gethostname()
print host

cur.execute("SELECT active, run_stages, temp_dir, cmtk_dir, template_dir FROM system_server WHERE host_name like '" + host + "'")
record = cur.fetchone()
print record
template = 'template.nrrd'
floatingImage = 'default.nrrd'
# record = db.system_server.find_one({'host_name': host})

if record:
  active = record[0]
  run_stage = record[1]
  tempfolder = str(record[2])
  cmtkdir = str(record[3])
  templatedir = str(record[4])

  cur.execute('SELECT file FROM system_template')
  record = cur.fetchone()
  print record
  if record:
    template = templatedir + str(record[0])

  print 'Settings loaded.'

  def initial(floatingImage, xformOUT=floatingImage.replace('.nrrd','_initial.xform'), template=template, mode='--principal-axes'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_initial.xform')
    print 'nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT)
    r = subprocess.call("nice %smake_initial_affine %s '%s' '%s' '%s'" % (cmtkdir, mode, template, floatingImage, xformOUT), shell=True)
    os.chmod(xformOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return xformOUT, r

  def affine(floatingImage, xformOUT=floatingImage.replace('.nrrd','_affine.xform'), xformIN=floatingImage.replace('.nrrd','_initial.xform'), template=template, scale='--dofs 6,9 --auto-multi-levels 4'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_affine.xform')
    if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_initial.xform')
    print 'nice %sregistration --initial %s %s -o %s %s %s' % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage)
    r = subprocess.call("nice %sregistration --initial '%s' %s -o '%s' '%s' '%s'" % (cmtkdir, xformIN, scale, xformOUT, template, floatingImage), shell=True)
    os.chmod(xformOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return xformOUT, r

  def warp(floatingImage, xformOUT=floatingImage.replace('.nrrd','_warp.xform'), xformIN=floatingImage.replace('.nrrd','_affine.xform'), template=template, settings='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
    if 'default' in xformOUT: xformOUT=floatingImage.replace('.nrrd','_warp.xform')
    if 'default' in xformIN: xformIN=floatingImage.replace('.nrrd','_affine.xform')
    print 'nice %swarp -o %s %s --initial %s %s %s' % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage)
    r = subprocess.call("nice %swarp -o '%s' %s --initial '%s' '%s' '%s'" % (cmtkdir, xformOUT, settings, xformIN, template, floatingImage), shell=True)
    os.chmod(xformOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return xformOUT, r

  def align(floatingImage, xform=floatingImage.replace('.nrrd','_warp.xform'), imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd'), template=template, settings=''):
    if 'default' in xform: xform=floatingImage.replace('.nrrd','_warp.xform')
    if 'default' in imageOUT: imageOUT=floatingImage.replace('.nrrd','_aligned.nrrd')
    print 'nice %sreformatx %s -o %s --floating %s %s %s' % (cmtkdir, settings, imageOUT, floatingImage, template, xform)
    r = subprocess.call("nice %sreformatx %s -o '%s' --floating '%s' '%s' '%s'" % (cmtkdir, settings, imageOUT, floatingImage, template, xform), shell=True)
    os.chmod(imageOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return imageOUT, r

  def checkDir(record):
    if not 'last_host' in record:
      record['last_host'] = 'roberts-mbp'
    if host == str(record['last_host']):
      return record
    else:
      cur.execute("SELECT active, run_stages, temp_dir, cmtk_dir, template_dir FROM system_server WHERE host_name like '" + host + "'")
      temprec = cur.fetchone()
      # temprec = db.system_server.find_one({'host_name': str(record['last_host'])})
      if temprec:
        # if 'use_settings_id' in temprec:
        #   tempSet_id = temprec['use_settings_id']
        #   temprec2 = db.system_setting.find_one({'_id': tempSet_id})
        #   if temprec2:
            # if 'temp_dir' in temprec2:
        prevtempfolder = temprec[2]
        print 'Replacing ' + str(prevtempfolder) + ' with ' + str(tempfolder) + ' in:'
        for key, value in record.items():
          # if key == 'original_nrrd':
          #   print '    Original nrrd data:'
          #   for k,v in record['original_nrrd'].items():
          #     if prevtempfolder in str(v):
          #       print '                ' + str(v)
          #       temp = str(v).replace(prevtempfolder,tempfolder)
          #       record['original_nrrd'][k]=temp
          # else:
          if prevtempfolder in str(value):
            print '    ' + str(value)
            temp = str(value).replace(prevtempfolder,tempfolder)
            record[key]=temp
        record['last_host'] = host
      return record

else:
  print 'No active records found for hostname:' + host + ' This could be due to your hostname changing check a server record exists for this machine.'
