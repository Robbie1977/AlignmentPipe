import os
import shutil
import stat
import subprocess
from socket import gethostname

import psycopg2

import nrrd

con = psycopg2.connect(host='bocian.inf.ed.ac.uk', database='alignment', user='aligner_admin', password='default99')

ori = ['LPS', 'RPI', 'RAS', 'LAI', 'PLI', 'PRS', 'ALS', 'ARI']  # X(>),Y(\/),Z(X).
orien = [
    str(x).replace('R', 'right-').replace('L', 'left-').replace('P', 'posterior-').replace('A', 'anterior-').replace(
        'S', 'superior').replace('I', 'inferior') for x in ori]
comp_orien = dict(zip(ori, orien))

cur = con.cursor()

adjust_thresh = 0.0035
setting_id = u'1'
host = gethostname()
print host

cur.execute(
    "SELECT active, run_stages, temp_dir, cmtk_dir, template_dir FROM system_server WHERE host_name like '" + host + "'")
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


    def initial(floatingImage, xformOUT=floatingImage.replace('.nrrd', '_initial.xform'), template=template,
                mode='--principal-axes'):
        if 'default' in xformOUT: xformOUT = floatingImage.replace('.nrrd', '_initial.xform')
        if (os.path.exists(template) and os.path.exists(floatingImage)):
            if os.path.exists(xformOUT):
                print 'removing old alignment %s' % (xformOUT)
                os.remove(xformOUT)
            print 'nice %smake_initial_affine %s %s %s %s' % (cmtkdir, mode, template, floatingImage, xformOUT)
            r = subprocess.call(
                "nice %smake_initial_affine %s '%s' '%s' '%s'" % (cmtkdir, mode, template, floatingImage, xformOUT),
                shell=True)
            try:
                os.chmod(xformOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            except:
                pass
        else:
            r = 99
        return xformOUT, r


    def affine(floatingImage, xformOUT=floatingImage.replace('.nrrd', '_affine.xform'),
               xformIN=floatingImage.replace('.nrrd', '_initial.xform'), template=template,
               scale='--dofs 6,9 --auto-multi-levels 4'):
        if 'default' in xformOUT: xformOUT = floatingImage.replace('.nrrd', '_affine.xform')
        if 'default' in xformIN: xformIN = floatingImage.replace('.nrrd', '_initial.xform')
        if (os.path.exists(xformIN) and os.path.exists(template) and os.path.exists(floatingImage)):
            if os.path.exists(xformOUT):
                print 'removing old alignment %s' % (xformOUT)
                shutil.rmtree(xformOUT)
            print 'nice %sregistration --initial %s %s -o %s %s %s' % (
                cmtkdir, xformIN, scale, xformOUT, template, floatingImage)
            r = subprocess.call("nice %sregistration --initial '%s' %s -o '%s' '%s' '%s'" % (
                cmtkdir, xformIN, scale, xformOUT, template, floatingImage), shell=True)
            try:
                os.chmod(xformOUT , 0o777)
                for root,dirs,_ in os.walk(xformOUT):
                    for d in dirs :
                        os.chmod(os.xformOUT.join(root,d) , 0o777)
            except:
                pass
        else:
            r = 99
        return xformOUT, r


    def warp(floatingImage, xformOUT=floatingImage.replace('.nrrd', '_warp.xform'),
             xformIN=floatingImage.replace('.nrrd', '_affine.xform'), template=template,
             settings='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1'):
        if 'default' in xformOUT: xformOUT = floatingImage.replace('.nrrd', '_warp.xform')
        if 'default' in xformIN: xformIN = floatingImage.replace('.nrrd', '_affine.xform')
        if (os.path.exists(xformIN) and os.path.exists(template) and os.path.exists(floatingImage)):
            if os.path.exists(xformOUT):
                print 'removing old alignment %s' % (xformOUT)
                shutil.rmtree(xformOUT)
            print 'nice %swarp -o %s %s --initial %s %s %s' % (
                cmtkdir, xformOUT, settings, xformIN, template, floatingImage)
            r = subprocess.call("nice %swarp -o '%s' %s --initial '%s' '%s' '%s'" % (
                cmtkdir, xformOUT, settings, xformIN, template, floatingImage), shell=True)
            try:
                os.chmod(xformOUT , 0o777)
                for root,dirs,_ in os.walk(xformOUT):
                    for d in dirs :
                        os.chmod(os.xformOUT.join(root,d) , 0o777)
            except:
                pass
        else:
            r = 99
        return xformOUT, r


    def align(floatingImage, xform=floatingImage.replace('.nrrd', '_warp.xform'),
              imageOUT=floatingImage.replace('.nrrd', '_aligned.nrrd'), template=template, settings=''):
        if 'default' in xform: xform = floatingImage.replace('.nrrd', '_warp.xform')
        if 'default' in imageOUT: imageOUT = floatingImage.replace('.nrrd', '_aligned.nrrd')
        if settings == None or 'None' in settings: settings = ''
        if (os.path.exists(xform) and os.path.exists(template) and os.path.exists(floatingImage)):
            if os.path.exists(imageOUT):
                print 'removing old alignment %s' % (imageOUT)
                os.remove(imageOUT)
            print 'nice %sreformatx %s -o %s --floating %s %s %s' % (
                cmtkdir, settings, imageOUT, floatingImage, template, xform)
            r = subprocess.call("nice %sreformatx %s -o '%s' --floating '%s' '%s' '%s'" % (
                cmtkdir, settings, imageOUT, floatingImage, template, xform), shell=True)
            try:
                data1, header1 = nrrd.read(template)
                data1, header2 = nrrd.read(imageOUT)
                header1['encoding'] = 'gzip'
                if header1['space directions'] == ['none', 'none', 'none']:
                    header1.pop("space directions", None)
                if os.path.exists(imageOUT):
                    os.remove(imageOUT)
                nrrd.write(imageOUT, data1, options=header1)
                os.chmod(imageOUT, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            except:
                pass
        else:
            r = 99
        return imageOUT, r


    def checkDir(record):
        if not 'last_host' in record:
            record['last_host'] = 'roberts-mbp'
        if host == str(record['last_host']):
            return record
        else:
            cur.execute(
                "SELECT active, run_stages, temp_dir, cmtk_dir, template_dir FROM system_server WHERE host_name like '" + host + "'")
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
                        temp = str(value).replace(prevtempfolder, tempfolder)
                        record[key] = temp
                record['last_host'] = host
            return record

else:
    print 'No active records found for hostname:' + host + ' This could be due to your hostname changing check a server record exists for this machine.'
    cwd = os.getcwd()
    if 'AlignmentPipe' in cwd:
        active = True
        runstages = '2,3,4'
        tempfolder = cwd.replace('AlignmentPipe', 'tmp/')
        cmtkdir = cwd.replace('VFB', 'VFBTools').replace('aligner', 'cmtk').replace('AlignmentPipe', 'bin/')
        templatedir = cwd.replace('VFB/aligner/AlignmentPipe', 'VFBTools/')
        uploaddir = cwd.replace('AlignmentPipe', 'uploads/')
        cur.execute(
            "INSERT INTO system_server (host_name, active, temp_dir, cmtk_dir, template_dir, upload_dir, run_stages) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [host, active, tempfolder, cmtkdir, templatedir, uploaddir, runstages])
        cur.connection.commit()
        print 'Server added to DB as inactive'
