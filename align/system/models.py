from django.db import models
import fnmatch
import os

# temp=['/tmp/']
temp=['/Volumes/Data0/tmp/']
TAGtemplate=['/robert/GIT/DrosAdultTAGdomains/template/Neuropil_LPS.nrrd']
cmtk=['/opt/local/lib/cmtk/bin/']
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
class Setting(models.Model):
    name = models.TextField(max_length=50, default='Drosophila,Adult,TAG,RobMac')
    temp_dir = models.TextField(max_length=1000, default=temp[-1])
    cmtk_dir = models.TextField(max_length=1000, default=cmtk[-1])
    template = models.TextField(max_length=1000, default=TAGtemplate[-1])
    initial_pass_level = models.CharField(max_length=10, default='0.30')
    final_pass_level = models.CharField(max_length=10, default='0.60')
    auto_balance_th = models.CharField(max_length=10, default='0.0035')
    def __str__(self):
        desc = str.split(str(self.name),',')
        return str(desc[3]) + ' settings for alignment of ' + str(desc[1]) + ' ' + str(desc[0]) + ' ' + str(desc[2])

class Server(models.Model):
    from socket import gethostname
    from system.models import Setting
    host_name = models.CharField(max_length=50, default=gethostname())
    run_stages = models.CharField(max_length=50, default='1,2,3,4,5,6')
    use_settings = models.ForeignKey(Setting)
    use_DB = models.CharField(max_length=100, default='localhost')
    active = models.BooleanField(default=False)
    def __str__(self):
        from images.models import stage
        setStages = str.split(str(self.run_stages),',')
        if self.active:
           serv = 'active'
        else:
           serv = 'inactive'
        return str(self.host_name) + ' is currently ' + serv + ' with settings [' + str(self.use_settings) + '] to run: ' + str([stage[int(x)] for x in setStages])
