import os, sys, nrrd, cmtk
from tiffile import TiffFile
import numpy as np


def reorientate(data,curOr='right-posterior-inferior',targOr='left-posterior-superior'):
  curOr = minOrien(curOr)
  targOr = minOrien(targOr)
  print '[' + curOr + ']-->[' + targOr + ']...'
  if curOr.find(targOr[0]) == 0:
     if curOr.find(targOr[1]) == 1:
       if curOr.find(targOr[2]) == 2:
         print curOr
         return data

  for i in range(0,3):
    if not curOr.find(targOr[i]) == i:
      if curOr.find(opositeOr(targOr[i])) > -1:
        data = np.swapaxes(data,curOr.find(opositeOr(targOr[i])),i)
        temp = list(curOr)
        temp[i] = opositeOr(targOr[i])
        temp[curOr.find(opositeOr(targOr[i]))] = curOr[i]
        curOr = ''.join(temp)
        print '-O->[' + curOr + ']->'
        del temp
      else:
        data = np.swapaxes(data,curOr.find(targOr[i]),i)
        temp = list(curOr)
        temp[i] = targOr[i]
        temp[curOr.find(targOr[i])] = curOr[i]
        curOr = ''.join(temp)
        print '-P->[' + curOr + ']->'
        del temp

  d = [1,1,1]
  for i in range(0,3):
    if curOr.find(opositeOr(targOr[i])) == i:
      d[i]=-1
      data = data[::d[0],::d[1],::d[2]]
      d[i]=1
      temp = list(curOr)
      temp[i]=targOr[i]
      curOr = ''.join(temp)
      print '-F->[' + curOr + ']->'
      del temp
  del d
  print '->[' + curOr + ']'
  return data



def minOrien(space):
  space = space.lower()
  space = space.replace('left','L')
  space = space.replace('right','R')
  space = space.replace('posterior','P')
  space = space.replace('anterior','A')
  space = space.replace('superior','S')
  space = space.replace('inferior','I')
  space = space.replace('-','')
  return space

def opositeOr(position):
  Or = {'R':'L','L':'R','P':'A','A':'P','S':'I','I':'S'}
  return Or[position]
