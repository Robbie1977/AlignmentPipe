import gc
import os
import stat
import time
from subprocess import check_call

import numpy as np

import NRRDtools.autoBalance as ab
import nrrd
import reorientate as ro
from cmtk import cur, tempfolder, active, run_stage, checkDir, host, comp_orien
from tiffile import TiffFile


def convRec(record):
    try:
        if not 'loading_host' in record:
            record['loading_host'] = 'roberts-mbp'
        if not record['loading_host'] == host:
            print 'Warning: ' + host + ' is not the loading host (' + record['loading_host'] + ')'
        if str(record['original_path']).endswith(os.path.sep):
            file = record['original_path'] + record['name'] + record['original_ext']
        else:
            file = record['original_path'] + os.path.sep + record['name'] + record['original_ext']
        print 'Converting ' + file
        if (os.path.exists(file) or os.path.exists(file + '.gz')):
            record['last_host'] = host
            if (os.path.exists(file + '.gz') and (not os.path.exists(file))):
                check_call(['gzip', '-d', file + '.gz'])
            if '.gz' in file:
                check_call(['gzip', '-df', file])
                file = str(file).replace('.gz', '')
                if str(record['original_ext']) == '.gz':
                    record['name'] = str(os.path.splitext(os.path.basename(file))[0])
                    record['original_ext'] = str(os.path.splitext(os.path.basename(file))[1])
            print 'Opening file: ' + file + '...'
            tif = TiffFile(file)
            image = tif.asarray()
            print 'Converting file: ' + file + '...'
            record = checkDir(record)
            if tif.is_lsm:
                metadata = tif[0].cz_lsm_scan_information
                voxelZ = metadata['plane_spacing']
                voxelY = metadata['line_spacing']
                voxelX = metadata['sample_spacing']
                header = {}
                header['encoding'] = 'gzip'
                header['space directions'] = [[float(voxelX), 0.0, 0.0], [0.0, float(voxelY), 0.0],
                                              [0.0, 0.0, float(voxelZ)]]
                header['space units'] = ['"microns"', '"microns"', '"microns"']
                # header['keyvaluepairs'] = dict(metadata)
                # print header
            else:
                metadata = tif[0].image_description
                # metadata = json.loads(metadata.decode('utf-8'))
                # voxel = metadata['Voxel size']
                # TBD: resolve zoxel size!
                voxelZ = 0.5
                voxelY = 0.5
                voxelX = 0.5
                header = {}
                header['encoding'] = 'gzip'
                header['space directions'] = [[float(voxelX), 0.0, 0.0], [0.0, float(voxelY), 0.0],
                                              [0.0, 0.0, float(voxelZ)]]
                header['space units'] = ['"px"', '"px"', '"px"']
                print(image.shape, image.dtype)
                if image.ndim > 4:
                    sh = np.array(image.shape)
                    rmdim = np.argmin(sh)
                    if sh[rmdim] > 1:
                        sh[rmdim] = np.max(sh)
                        rmdim = np.argmin(sh)
                    image = np.max(image, axis=rmdim)
                    print 'slimmed down to:'
                    print(image.shape, image.dtype)

                print metadata
                # TBD: add voxel size data
                # header['keyvaluepairs'] = dict(metadata)
            tif.close()
            check_call(['gzip', '-f', file])
            image = np.squeeze(image)
            sh = np.array(np.shape(image))
            ch = np.argmin(sh)
            iy = np.argmax(sh)
            sh[iy] = 0
            ix = np.argmax(sh)
            sh[ix] = 0
            iz = np.argmax(sh)
            sh = np.shape(image)
            # move channel to last axis:
            image = np.swapaxes(image, ch, -1)
            # move smalest (Z) axis to last axis before channel:
            image = np.swapaxes(image, iz, -2)
            # swap X & Y to match NRRD standard order for saving:
            image = np.swapaxes(image, 0, 1)
            print record['name'] + record['original_ext'] + ' - ' + str(np.shape(image))
            rt = 0
            mt = 0
            sg = 0
            bg = 0
            cur.execute(
                "SELECT system_template.orientation FROM system_template, system_setting, images_alignment WHERE images_alignment.id = %s AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id",
                [record['id']])
            tempOrien = cur.fetchone()[0]
            cur.execute(
                "SELECT system_setting.auto_balance_th FROM system_template, system_setting, images_alignment WHERE images_alignment.id = %s AND images_alignment.settings_id = system_setting.id AND system_setting.template_id = system_template.id",
                [record['id']])
            tempTresh = cur.fetchone()[0]
            if 'orig_orientation' not in record.keys():
                if sh[ch] == 2:
                    record['orig_orientation'] = comp_orien[tempOrien]
                else:
                    record['orig_orientation'] = 'right-posterior-inferior'  # needs to be set at load
            if record['orig_orientation'] == '':
                if sh[ch] == 2:
                    record['orig_orientation'] = comp_orien[tempOrien]
                else:
                    record['orig_orientation'] = 'right-posterior-inferior'  # needs to be set at load
            header['space'] = comp_orien[tempOrien]
            for c in xrange(0, sh[ch]):
                upd = {}
                chan, Nbound, hist = ab.AutoBalance(np.squeeze(image[:, :, :, c]), threshold=tempTresh, background=0)
                print 'Ch' + str(c + 1) + ' - ' + str(np.shape(chan))
                Sname = tempfolder + record['name'] + '_Ch' + str(c + 1) + '.nrrd'

                if not record['orig_orientation'] == comp_orien[tempOrien]:
                    chan = ro.reorientate(np.uint8(chan), curOr=record['orig_orientation'],
                                          targOr=comp_orien[tempOrien])
                else:
                    chan = np.uint8(chan)

                if not ((record['crop_xyz'] is None) or (record['crop_xyz'] is '')):
                    cut = map(int, str(record['crop_xyz']).replace('[', '').replace(']', '').split(','))
                    cut = np.array(cut)
                    if np.sum(cut) > 0:
                        print 'cropping: (' + str(cut) + ')...'
                        sh = np.shape(chan)
                        print sh
                        chan = chan[cut[0]:sh[0] - cut[1], cut[2]:sh[1] - cut[3], cut[4]:sh[2] - cut[5]]
                        print np.shape(chan)

                print 'saving...'
                nrrd.write(Sname, chan, options=header)
                upd.update(
                    {'image_id': record['id'], 'channel': + int(c + 1), 'file': str(Sname).replace(tempfolder, ''),
                     'pre_histogram': list(hist), 'new_min': int(Nbound['min']), 'new_max': int(Nbound['max'])})
                cur.execute(
                    "SELECT count(*) FROM images_original_nrrd WHERE image_id = %(image_id)s AND channel = %(channel)s",
                    upd)
                r = cur.fetchone()[0]
                if r > 0:
                    cur.execute(
                        "UPDATE images_original_nrrd SET file = %(file)s, pre_hist = %(pre_histogram)s, new_min = %(new_min)s, new_max = %(new_max)s, is_index = False WHERE image_id = %(image_id)s AND channel = %(channel)s",
                        upd)
                    cur.connection.commit()
                else:
                    cur.execute(
                        "INSERT INTO images_original_nrrd (image_id, channel, file, pre_hist, new_min, new_max, is_index) VALUES (%(image_id)s, %(channel)s, %(file)s, %(pre_histogram)s, %(new_min)s, %(new_max)s, False)",
                        upd)
                    cur.connection.commit()
                try:
                    os.chmod(Sname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                except:
                    pass
                ct = sum(chan[chan > 20])
                if ct > rt:
                    rt = ct
                    bg = c + 1
                if mt == 0:
                    mt = ct
                    sg = c + 1
                if ct < mt:
                    mt = ct
                    sg = c + 1
            print 'BG: ' + str(bg) + ', SG: ' + str(sg)
            if record['background_channel'] == 0:
                record['background_channel'] = bg
            if record['signal_channel'] == 0:
                record['signal_channel'] = sg
            record['alignment_stage'] = 2
            # record.update({'original_nrrd': upd})
            record['max_stage'] = 2
            # collection.save(record)

            print 'conversion complete.'
            del upd, hist, chan, Nbound, tif, image, sh, ch, iy, ix, iz, Sname, rt, bg, ct, mt, sg
        else:
            record['alignment_stage'] = 1001
            if record['notes'] is None:
                record['notes'] = time.strftime(
                    "%c") + ' Error finding file ' + file + ' on ' + host
            else:
                record['notes'] = record['notes'] + '\n' + time.strftime(
                    "%c") + ' Error finding file ' + file + ' on ' + host
    except Exception, e:
        print str(e)
        record['alignment_stage'] = 0
        if record['notes'] is None:
            record['notes'] = time.strftime(
                "%c") + ' Error with handling uploaded file by ' + host
        else:
            record['notes'] = record['notes'] + '\n' + time.strftime(
                "%c") + ' Error with handling uploaded file by ' + host
    return record


def convert(name):
    cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 1 AND name like %s", [name])
    records = cur.fetchall()
    key = []
    for desc in cur.description:
        key.append(desc[0])
    for line in records:
        record = dict(zip(key, line))
        # remove image from stack before processing:
        cur.execute("UPDATE images_alignment SET alignment_stage = 1001, last_host = %s WHERE id = %s ",
                    [str(host), str(record['id'])])
        cur.connection.commit()
        r = convRec(record)
        u = str(record['id']) + ' -> '
        for k, v in record.items():
            if not (k == 'id' or v == None or v == 'None'):
                cur.execute("UPDATE images_alignment SET " + str(k) + "=%s WHERE id = %s ", [v, record['id']])
                u = u + str(k) + '=' + str(v) + ', '
        print u
        cur.connection.commit()
        gc.collect()


if __name__ == "__main__":
    if active and '1' in run_stage:
        cur.execute("SELECT name FROM images_alignment WHERE alignment_stage = 1 ORDER BY id")
        records = cur.fetchall()
        total = len(records)
        if total == 0:
            # add any paused records to the active list
            cur.execute(
                "UPDATE images_alignment SET alignment_stage = 1 FROM (SELECT id FROM images_alignment WHERE alignment_stage = 2001 ORDER BY id LIMIT 2) s WHERE s.id = images_alignment.id")
            # clear old failed alignments:
            cur.execute(
                "UPDATE images_alignment SET alignment_stage = 1 WHERE last_host = %s AND alignment_stage = 1001",
                [str(host)])
            cur.connection.commit()
            gc.collect()
        count = 0
        for line in records:
            count += 1
            print 'Converting: ' + str(count) + ' of ' + str(total)
            convert(line[0])
        print 'done'
    else:
        print 'inactive or stage 1 not selected'
