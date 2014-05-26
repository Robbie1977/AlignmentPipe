from pymongo import MongoClient
import os, sys, nrrd
from tiffile import TiffFile
import numpy as np

client = MongoClient('localhost', 27017)
db = client.alignment
collection = db.processing

param = db.param.temp.find()
for record in param:
  if 'folder' in record:
    tempfolder = record['folder']


def AutoBalance(data,threshold=0.00035,background=0):
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
            m = x-1
            break
    for x in range(np.shape(bins)[0]-1,0,-1):
        if np.sum(histogram[x:]) > th:
            M = x
            break
    data[data>M]=M
    data[data<m]=m
    dataA=np.round((data-m)*(255.0/(M-m)))
    return (dataA, np.array([m, M], dtype=np.uint32), np.array([bins,histogram],dtype=np.uint32))


for record in collection.find({'original_nrrd': { '$exists': False } }):
  file = record['original_path'] + os.path.sep + record['name'] + record['original_ext']
  if os.path.exists(file):
    tif = TiffFile(file)
    image = tif.asarray()
    image = np.squeeze(image)
    sh = np.array(np.shape(image))
    ch = np.argmin(sh)
    iy = np.argmax(sh)
    sh[iy] = 0
    ix = np.argmax(sh)
    sh[ix] = 0
    iz = np.argmax(sh)
    sh = np.shape(image)
    image = np.swapaxes(image,ch,-1)
    image = np.swapaxes(image,iz,-2)
    print record['name'] + record['original_ext'] + ' - ' + str(np.shape(image))
    upd = {}
    print record
    for c in xrange(0,sh[ch]):
      chan, Nbound, hist = AutoBalance(np.squeeze(image[:,:,:,c]))
      Sname = tempfolder + os.path.sep + record['name'] + '_Ch' + str(c+1) + '.nrrd'
      nrrd.write(Sname,np.uint8(chan))
      upd.update({"Ch" + str(c+1) + "_file": Sname , "Ch" + str(c+1) + "_histogram": dict(zip(hist[0,:],hist[1,:])), "Ch" + str(c+1) + "_new_boundary":{"min": Nbound[0],"max": Nbound[1]}})
    print upd
    record.update({'original_nrrd': upd })
    print record
    collection.save(record)
    tif.close()
    del upd, hist, chan, Nbound, tif, image, sh, ch, iy, ix, iz, Sname
