from django.db import models
import fnmatch
import os
from socket import gethostname

host = gethostname()

ori = ['LPS','RPI','RAS','LAI','PLI','PRS','ALS','ARI'] #X(>),Y(\/),Z(X).
orien = [str(x).replace('R','right-').replace('L','left-').replace('P','posterior-').replace('A','anterior-').replace('S','superior').replace('I','inferior') for x in ori]
comp_orien = dict(zip(ori,orien))
orien = zip(orien,orien)
conv_orien = dict(zip(comp_orien.values(),comp_orien.keys()))

# temp=['/tmp/']
temp=['/disk/data/VFB/aligner/tmp/']
updir=['/disk/data/VFB/aligner/uploads/']
templatedir=['/disk/data/VFBTools/']
TAGtemplate=['DrosAdultTAGdomains/template/Neuropil_LPS.nrrd']
cmtk=['/disk/data/VFBTools/cmtk/bin/']
# TAGtemplate = ['PATH/Neuropil_LPS.nrrd']
# for root, dirnames, filenames in os.walk(os.path.sep):
#   if not os.path.isfile(TAGtemplate[-1]):
#     for filename in fnmatch.filter(filenames, 'Neuropil_LPS.nrrd'):
#         TAGtemplate.append(os.path.join(root, filename))
#         break
#   if not os.path.exists(cmtk[-1]):
#     for filename in fnmatch.filter(filenames, 'make_initial_affine'):
#         cmtk.append(root)
#         break
#   if not os.path.exists(temp[-1]):
#     for dirnames in fnmatch.filter(dirnames, 'align_temp'):
#         temp.append(root)
#         break

# Create your models here.

class Template(models.Model):
    name = models.CharField(max_length=50, default='Drosophila,Adult,TAG,LPS')
    orientation = models.CharField(max_length=50, choices=comp_orien.items(), default='LPS')
    file = models.TextField(max_length=1000, default=TAGtemplate[-1])
    image = models.TextField(max_length=1000, default='/static/waiting.gif')
    def __str__(self):
        from images.models import comp_orien, conv_orien
        parts = str(self.name).split(',')
        return 'Template for the ' + parts[2] + ' of the ' + parts[1].lower() + ' ' + parts[0]
    def temp_image(self):
        return '<img src="/images/nrrd/template/%s"/>' % str(self.id)
    temp_image.short_description = 'template image for reference'
    temp_image.allow_tags = True


class Setting(models.Model):
    name = models.TextField(max_length=50, default='Drosophila,Adult,TAG,General')
    template = models.ForeignKey(Template, default=1)
    cmtk_initial_var = models.CharField(max_length=100, default='--principal-axes')
    cmtk_affine_var = models.CharField(max_length=100, default='--dofs 6,9 --auto-multi-levels 4')
    cmtk_warp_var = models.CharField(max_length=100, default='--grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.2 --refine 4 --energy-weight 1e-1')
    cmtk_align_var  = models.CharField(max_length=100, default='', blank=True)
    initial_pass_level = models.CharField(max_length=10, default='0.30')
    final_pass_level = models.CharField(max_length=10, default='0.60')
    auto_balance_th = models.CharField(max_length=10, default='0.0035')
    def __str__(self):
        desc = str.split(str(self.name),',')
        return str(desc[3]) + ' settings for alignment of ' + str(desc[1]) + ' ' + str(desc[0]) + ' ' + str(desc[2])

class Server(models.Model):
    host_name = models.CharField(max_length=50, default=host, unique=True)
    active = models.BooleanField(default=False)
    run_stages = models.CommaSeparatedIntegerField(max_length=255, blank=True, default=[1,2,3,4,5,6])
    temp_dir = models.TextField(max_length=1000, default=temp[-1])
    cmtk_dir = models.TextField(max_length=1000, default=cmtk[-1])
    template_dir = models.TextField(max_length=1000, default=templatedir[-1])
    upload_dir = models.TextField(max_length=1000, default=updir[-1])
    # use_db = models.CharField(max_length=100, default='bocian.inf.ed.ac.uk')
    def __str__(self):
        from images.models import stage
        setStages = str(self.run_stages).split(',')
        if self.active:
           serv = 'active'
        else:
           serv = 'inactive'
        if setStages == ['None']:
          return str(self.host_name) + ' is currently ' + serv + ' to run: [Nothing!]'
        else:
          return str(self.host_name) + ' is currently ' + serv + ' to run: ' + str([stage[int(x)] for x in setStages])



def checkDir(record):
  if record.last_host == '':
    record.last_host = 'roberts-mbp'
  if host == str(record.last_host):
    return record
  else:
    oldSerRec = Server.objects.get(host_name=record.last_host)
    if oldSerRec:
      curSetRec = Setting.objects.get(id=record.settings.id)
      if curSetRec:
        curSerRec = Server.objects.get(host_name=host)
        if curSerRec:
          record.temp_initial_nrrd = str(record.temp_initial_nrrd).replace(oldSerRec.temp_dir,curSerRec.temp_dir)
          record.aligned_bg = str(record.aligned_bg).replace(oldSerRec.temp_dir,curSerRec.temp_dir)
          record.aligned_sg = str(record.aligned_sg).replace(oldSerRec.temp_dir,curSerRec.temp_dir)
          record.aligned_ac1 = str(record.aligned_ac1).replace(oldSerRec.temp_dir,curSerRec.temp_dir)
          record.last_host = host
    return record


tempfolder = str(Server.objects.filter(host_name=host).values('temp_dir')[0]['temp_dir'])
