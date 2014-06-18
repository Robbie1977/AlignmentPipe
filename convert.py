from pymongo import MongoClient
import os, sys, nrrd, json
from tiffile import TiffFile
import numpy as np
import bson
import reorientate as ro
from cmtk import cur, tempfolder, active, run_stage, adjust_thresh, checkDir, host, comp_orien

def AutoBalance(data,threshold=adjust_thresh,background=0):
    bins=np.unique(data)
    binc=np.bincount(data.flat)
    histogram=binc[binc>0]
    del binc
    if background in bins:
        i = where(bins==background)
        v = bins[i][0]
        c = histogram[i][0]
        th=np.int(((np.sum(histogram)-histogram[i][0])/np.shape(data)[2])*threshold)
    else:
        th=np.int((np.sum(histogram)/np.shape(data)[2])*threshold)
    m=np.min(bins)
    M=np.max(bins)
    for x in range(1,np.shape(bins)[0]-1):
        if np.sum(histogram[:x]) > th:
            m = bins[x-1]
            break
    for x in range(np.shape(bins)[0]-1,0,-1):
        if np.sum(histogram[x:]) > th:
            M = bins[x]
            break
    data[data>M]=M
    data[data<m]=m
    dataA=np.round((data-m)*(255.0/(M-m)))
    hist=np.zeros(255)
    for i in range(0,np.shape(bins)[0]-1):
        hist[bins[i]]=histogram[i]
    return (dataA, {'min': int(m),'max': int(M)}, hist)

def convRec(record):
  if not 'loading_host' in record:
    record['loading_host'] = 'roberts-mbp'
  if not record['loading_host'] == host:
    print 'Warning: ' + host + ' is not the loading host (' + record['loading_host'] + ')'
  file = record['original_path'] + os.path.sep + record['name'] + record['original_ext']
  print 'Converting ' + file
  if os.path.exists(file):
    tif = TiffFile(file)
    image = tif.asarray()
    record = checkDir(record)
    if tif.is_lsm:
      metadata = tif[0].cz_lsm_scan_information
      voxelZ = metadata['plane_spacing']
      voxelY = metadata['line_spacing']
      voxelX = metadata['sample_spacing']
      header = {}
      header['encoding'] = 'gzip'
      header['space directions'] = [[float(voxelX),0.0,0.0],[0.0,float(voxelY),0.0],[0.0,0.0,float(voxelZ)]]
      header['space units'] = ['"microns"', '"microns"', '"microns"']
      # header['keyvaluepairs'] = dict(metadata)
      # print header
    else:
      metadata = tif[0].image_description
      metadata = json.loads(metadata.decode('utf-8'))
      print(image.shape, image.dtype, metadata['microscope'])
      print metadata
      header = {}
      # TBD: add voxel size data
      # header['keyvaluepairs'] = dict(metadata)
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
    image = np.swapaxes(image,ch,-1)
    # move smalest (Z) axis to last axis before channel:
    image = np.swapaxes(image,iz,-2)
    # swap X & Y to match NRRD standard order for saving:
    image = np.swapaxes(image,0,1)
    print record['name'] + record['original_ext'] + ' - ' + str(np.shape(image))
    rt = 0
    mt = 0
    sg = 0
    bg = 0
    cur.execute("SELECT system_template.orientation FROM system_template, images_alignment WHERE images_alignment.id = %s", [record['id']])
    tempOrien = cur.fetchone()[0]
    if 'orig_orientation' not in record.keys():
      if sh[ch] == 2:
        record['orig_orientation']=comp_orien[tempOrien]
      else:
        record['orig_orientation']='right-posterior-inferior' # needs to be set at load

    header['space'] = comp_orien[tempOrien]
    for c in xrange(0,sh[ch]):
      upd = {}
      chan, Nbound, hist = AutoBalance(np.squeeze(image[:,:,:,c]))
      print 'Ch' + str(c+1) + ' - ' + str(np.shape(chan))
      Sname = tempfolder + record['name'] + '_Ch' + str(c+1) + '.nrrd'

      if not record['orig_orientation'] == comp_orien[tempOrien]:
        chan = ro.reorientate(np.uint8(chan), curOr=record['orig_orientation'], targOr=comp_orien[tempOrien])
      else:
        chan = np.uint8(chan)
      print 'saving...'
      nrrd.write(Sname,chan, options=header)
      upd.update({'image_id': record['id'], 'channel': + int(c+1), 'file': str(Sname), 'pre_histogram': list(hist), 'new_min': int(Nbound['min']), 'new_max': int(Nbound['max'])})
      cur.execute("INSERT INTO images_original_nrrd (image_id, channel, file, pre_histogram, new_min, new_max) VALUES (%(image_id)s, %(channel)s, %(file)s, %(pre_histogram)s, %(new_min)s, %(new_max)s)", upd)
      cur.connection.commit()
      ct = sum(chan[chan>20])
      if ct > rt:
        rt = ct
        bg = c+1
      if mt == 0:
        mt = ct
        sg = c+1
      if ct < mt:
        mt = ct
        sg = c+1
    print 'BG: ' + str(bg) + ', SG: ' + str(sg)
    record['background_channel'] = bg
    record['signal_channel'] = sg
    record['alignment_stage'] = 2
    # record.update({'original_nrrd': upd})
    record['max_stage'] = 2
    # collection.save(record)
    tif.close()
    print 'conversion complete.'
    del upd, hist, chan, Nbound, tif, image, sh, ch, iy, ix, iz, Sname, rt, bg, ct, mt, sg
    return record

def convert(name):
  cur.execute("SELECT * FROM images_alignment WHERE alignment_stage = 1 AND name like %s", [name])
  records = cur.fetchall()
  key = []
  for desc in cur.description:
      key.append(desc[0])
  for line in records:
      record = dict(zip(key,line))
      r = convRec(record)
      u = ''
      for k, v in record:
        if not k == 'id':
          if not k == key[0]:
            u = u + ', '
          if type(v) == type(''):
            u = u + str(k) + " = '" + str(v) + "'"
          else:
            u = u + str(k) + " = " + str(v)
      cur.execute("UPDATE alignment_stage SET (%s) WHERE id = %s ", [u, str(record['id'])])
      cur.connection.commit()

if __name__ == "__main__":
  if active and '1' in run_stage:
    cur.execute("SELECT name FROM images_alignment WHERE alignment_stage = 1")
    records = cur.fetchall()
    for line in records:
      convert(line[0])
    print 'done'
  else:
    print 'inactive or stage 1 not selected'
