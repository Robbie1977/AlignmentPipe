from pymongo import MongoClient
import os, sys, nrrd
from tiffile import TiffFile
import numpy as np

client = MongoClient('localhost', 27017)
db = client.alignment
collection = db.processing
param = db.param

def AutoBalance(data,threshold=0.00035,background=0):
    bins=np.unique(data)
    binc=np.bincount(data.flat)
    histogram=binc[binc>0]
    del binc
    if background in bins:
        i = where(bins==background)
        v = bins[i][0]
        c = histogram[i][0]
        th=int(((sum(histogram)-histogram[i][0])/shape(data)[2])*threshold)
    else:
        th=int((sum(histogram)/shape(data)[2])*threshold)
    m=min(bins)
    M=max(bins)
    for x in range(1,shape(bins)[0]-1):
        if sum(histogram[:x]) > th:
            m = x-1
            break
    for x in range(shape(bins)[0]-1,0,-1):
        if sum(histogram[x:]) > th:
            M = x
            break
    data[data>M]=M
    data[data<m]=m
    dataA=round((data-m)*(255.0/(M-m)))
    return (dataA, array([m, M], dtype=uint32), array([bins,histogram],dtype=uint32))


for record in collection.find({'original_nrrd': { '$exists': False } }):
  file = record['original_path'] + os.path.sep + record['name'] + record['original_ext']
  if os.path.exists(file):
    tif = TiffFile(file)
    image = tif.asarray()
    image = np.squeeze(image)
    sh = np.shape(image)
    ch = np.argmin(sh)
    iy = np.argmax(sh)
    sh[iy] = 0
    ix = np.argmax(sh)
    sh[ix] = 0
    iz = np.argmax(sh)
    sh = np.shape(image)
    Simage = np.swapaxes(image,ix,iy,iz,ch)
    for c in xrange(0,sh[ch]):
      chan, Nbound, hist = AutoBalance(np.squeeze(Simage[:,:,:,c]))
      Sname[c] = param.find_one('name':'temp')['value'] + os.path.sep + record['name'] + '_Ch' + str(c) + '.nrrd'
      nrrd.write(Sname[c],np.uint8(chan))
      
    tif.close()
