import numpy as np
import sys
import nrrd

if (len(sys.argv) < 3):
    print 'Error: missing arguments!'
    print 'e.g. python SortNG-SG.py NG.nrrd SG.nrrd'
else:

    print 'Checking intensity for ', str(sys.argv[1]), ' against the intensity of ', str(sys.argv[2]), '...'
  
    readdata, op1 = nrrd.read(str(sys.argv[1]))
    
    im1 = readdata
    
    readdata, op2 = nrrd.read(str(sys.argv[2])) 
    im2 = readdata
      
    if (im1.size <> im2.size):
        print '\n\nError: Images must be the same size!!'
    else:
        sm1=np.sum(im1)
        sm2=np.sum(im2)        
        print 'NG:%s SG:%s' %(str(sm1), str(sm2))
        if (sm1 < sm2):
            print 'swapping the files due to inconsistency in assignment...'
            nrrd.write(str(sys.argv[1]), im2, options=op2)
            nrrd.write(str(sys.argv[2]), im1, options=op1)
        else:
            print 'images appear to be correctly assigned'
        print 'Done.'
        
  

