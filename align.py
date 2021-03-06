import cmtk
import gc
import os

import numpy as np

import warpScoring.CheckImages as ci
import warpScoring.slicescore as slicescore
from cmtk import cur, tempfolder, active, run_stage, template, checkDir, host, templatedir


def alignRec(record, template=template, bgfile='image_Ch1.nrrd', alignSet='', threshold=0.6):
    record = checkDir(record)
    record['last_host'] = host
    print 'Finalising alignment for: ' + record['name']
    # bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
    record['aligned_bg'], r = cmtk.align(bgfile, template=template, settings=alignSet)
    record['aligned_avgslice_score'] = str(
        ci.rateOne(record['aligned_bg'], results=None, methord=slicescore.avgOverlapCoeff, template=template))
    record['aligned_slice_score'] = str(
        ci.rateOne(record['aligned_bg'], results=None, methord=slicescore.OverlapCoeff, template=template))
    record['aligned_score'] = str(
        np.mean([np.float128(record['aligned_avgslice_score']), np.float128(record['aligned_slice_score'])]))
    # Note: np.float128 array score converted to string as mongoDB only supports float(64/32 dependant on machine).
    record['aligned_bg'] = str(record['aligned_bg']).replace(tempfolder, '')
    print 'Result: ' + record['aligned_score']
    if record['aligned_score'] > threshold:
        record['alignment_stage'] = 6
        print 'Passed!'
    else:
        record['alignment_stage'] = 0
        print 'Failed!'
    if r > 0:
        print 'Error Code:' + str(r)
        record['alignment_stage'] = 0
    record['max_stage'] = 6
    return record


def alignRem(record, template=template, chfile='image_Ch1.nrrd', alignSet=''):
    record = checkDir(record)
    print 'Aligning signal, etc. for: ' + record['name']
    record['last_host'] = host
    # bgfile = record['original_nrrd'][('Ch' + str(record['background_channel']) + '_file')]
    # sgfile = record['original_nrrd'][('Ch' + str(record['signal_channel']) + '_file')]
    # a=0
    # for i in range(1,6):
    # if not i == record['background_channel']:
    #   if i == record['signal_channel']:
    if record['ac1_channel'] < 1:
        for i in range(1, 4):
            print 'Checking for AC1 in channel ' + str(i)
            if not (i == int(record['signal_channel']) or i == int(record['background_channel'])):
                record['ac1_channel'] = i
                print 'Set AC1 Channel to ' + str(i)
    r = 0
    sgchan = '_Ch' + str(record['signal_channel'])
    bgchan = '_Ch' + str(record['background_channel'])
    acchan = '_Ch' + str(record['ac1_channel'])
    chfile = chfile.replace(bgchan, acchan).replace(acchan, sgchan)
    if os.path.isfile(chfile):
        record['aligned_sg'], r = cmtk.align(chfile, xform=chfile.replace(sgchan + '.nrrd', bgchan + '_warp.xform'),
                                             template=template, settings=alignSet)
        record['alignment_stage'] = 7
        record['max_stage'] = 7
        record['aligned_sg'] = str(record['aligned_sg']).replace(tempfolder, '')
    else:
        print chfile + ' not found'
        r = 5
    chfile = chfile.replace(sgchan, acchan)
    if os.path.isfile(chfile):
        record['aligned_ac1'], r = cmtk.align(chfile, xform=chfile.replace(acchan + '.nrrd', bgchan + '_warp.xform'),
                                              template=template, settings=alignSet)
        record['max_stage'] = 7
        record['aligned_ac1'] = str(record['aligned_ac1']).replace(tempfolder, '')
    else:
        print chfile + ' not found'

    if r > 0:
        print 'Error code:' + str(r)
        record['alignment_stage'] = 0
    return record


def align(name, template=template, bgfile='image_Ch1.nrrd', alignSet='', passLevel=0.6):
    cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 5 AND name like %s", [name])
    records = cur.fetchall()
    key = []
    for desc in cur.description:
        key.append(desc[0])
    for line in records:
        record = dict(zip(key, line))
        # clear old failed alignments:
        cur.execute("UPDATE images_alignment SET alignment_stage = 5 WHERE last_host = %s AND alignment_stage = 1005",
                    [str(host)])
        cur.connection.commit()
        # remove image from stack before processing:
        cur.execute("UPDATE images_alignment SET alignment_stage = 1005, last_host = %s WHERE id = %s ",
                    [str(host), str(record['id'])])
        cur.connection.commit()
        record = alignRec(record, template, bgfile, alignSet, passLevel)
        u = str(record['id']) + ' -> '
        for k, v in record.items():
            if not (k == 'id' or v == None or v == 'None'):
                cur.execute("UPDATE images_alignment SET " + str(k) + "=%s WHERE id = %s ", [v, record['id']])
                u = u + str(k) + '=' + str(v) + ', '
        print u
        cur.connection.commit()
        gc.collect()

    cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 6 AND name like %s", [name])
    records = cur.fetchall()
    key = []
    for desc in cur.description:
        key.append(desc[0])
    for line in records:
        record = dict(zip(key, line))
        # clear old failed alignments:
        cur.execute("UPDATE images_alignment SET alignment_stage = 6 WHERE last_host = %s AND alignment_stage = 1006",
                    [str(host)])
        cur.connection.commit()
        # remove image from stack before processing:
        cur.execute("UPDATE images_alignment SET alignment_stage = 1006, last_host = %s WHERE id = %s ",
                    [str(host), str(record['id'])])
        cur.connection.commit()
        record = alignRem(record, template, bgfile, alignSet)
        u = str(record['id']) + ' -> '
        for k, v in record.items():
            if not (k == 'id' or v == None or v == 'None'):
                cur.execute("UPDATE images_alignment SET " + str(k) + "=%s WHERE id = %s ", [v, record['id']])
                u = u + str(k) + '=' + str(v) + ', '
        print u
        cur.connection.commit()
        gc.collect()


if __name__ == "__main__":
    if active and '5' in run_stage:
        cur.execute(
            "SELECT images_alignment.name, system_template.file, images_original_nrrd.file, system_setting.cmtk_align_var, system_setting.final_pass_level FROM images_alignment, system_template, system_setting, images_original_nrrd WHERE alignment_stage = 5 AND images_original_nrrd.channel = images_alignment.background_channel AND images_original_nrrd.image_id = images_alignment.id AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id ORDER BY images_alignment.id")
        records = cur.fetchall()
        total = len(records)
        if total == 0:
            cur.execute(
                "UPDATE images_alignment SET alignment_stage = 5 FROM (SELECT id FROM images_alignment WHERE alignment_stage = 2005 ORDER BY id LIMIT 2) s WHERE s.id = images_alignment.id")
            cur.connection.commit()
            gc.collect()
        count = 0
        print records
        for line in records:
            count += 1
            print 'Warp alignment: ' + str(count) + ' of ' + str(total)
            align(line[0], template=(templatedir + line[1]), bgfile=(tempfolder + line[2]), alignSet=line[3],
                  passLevel=line[4])
        print 'done'
    else:
        print 'inactive or stage 5 not selected'

    if active and '6' in run_stage:
        cur.execute(
            "SELECT images_alignment.name, system_template.file, images_original_nrrd.file, system_setting.cmtk_align_var FROM images_alignment, system_template, system_setting, images_original_nrrd WHERE alignment_stage = 6 AND images_original_nrrd.channel = images_alignment.signal_channel AND images_original_nrrd.image_id = images_alignment.id AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id ORDER BY images_alignment.id")
        records = cur.fetchall()
        total = len(records)
        if total == 0:
            cur.execute(
                "UPDATE images_alignment SET alignment_stage = 6 FROM (SELECT id FROM images_alignment WHERE alignment_stage = 2006 ORDER BY id LIMIT 2) s WHERE s.id = images_alignment.id")
            cur.connection.commit()
            gc.collect()
        count = 0
        print records
        for line in records:
            count += 1
            print 'Warp alignment: ' + str(count) + ' of ' + str(total)
            align(line[0], template=(templatedir + line[1]), bgfile=(tempfolder + line[2]), alignSet=line[3])
        print 'done'
    else:
        print 'inactive or stage 6 not selected'
