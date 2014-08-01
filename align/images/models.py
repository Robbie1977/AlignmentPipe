from django.db import models
from socket import gethostname
from django.contrib.auth.models import User

import os

host = gethostname()

stage = {0: 'failed (check settings and restart)',1:'preprocessing', 1001:'preprocessing image stack', 2:'initial alignment', 1002:'calculating initial alignment', 3:'affine alignment', 1003:'processing affine alignment', 4:'final warp alignment', 1004:'processing warp alignment', 5:'checking alignment', 1005:'aligning BG channel', 6: 'aligning other channels', 1005:'aligning all channel using BG warp', 7: 'alignment done', 10: 'request merged tif',  1010: 'creating merged tif', 20: 'merged tif created'}
comp = {0: 'awaiting processing',1:'convertion complete', 2:'preprocessing complete', 3:'initial alignment complete', 4:'affine alignment complete', 5:'final warp complete', 6: 'background alignment complete', 7: 'all channels aligned', 10: 'merged tif requested', 20: 'merged tif created'}
chan = {0: 'to be calculated', 1:'Channel 1', 2:'Channel 2', 3:'Channel 3'}
ori = ['LPS','RPI','RAS','LAI','PLI','PRS','ALS','ARI'] #X(>),Y(\/),Z(X).
orien = [str(x).replace('R','right-').replace('L','left-').replace('P','posterior-').replace('A','anterior-').replace('S','superior').replace('I','inferior') for x in ori]
comp_orien = dict(zip(ori,orien))
orien = zip(orien,orien)
conv_orien = dict(zip(comp_orien.values(),comp_orien.keys()))
# Create your models here.

class Alignment(models.Model):
    import system.models
    #from users.models import User
    #from system.models import Setting
    name = models.CharField(max_length=500)
    settings = models.ForeignKey('system.Setting', default=1)
    max_stage = models.IntegerField(choices=comp.items(), default=0)
    last_host = models.CharField(max_length=100, blank=True, default=host)
    aligned_score = models.CharField(max_length=20, blank=True)
    alignment_stage = models.IntegerField(choices=stage.items(), default=1)
    orig_orientation = models.CharField(max_length=50, choices=orien, default='left-posterior-superior', blank=True)
    loading_host = models.CharField(max_length=100, blank=True)
    original_ext = models.CharField(max_length=10)
    original_path = models.TextField(max_length=1000)
    temp_initial_nrrd = models.TextField(max_length=1000, blank=True)
    temp_initial_score = models.CharField(max_length=20, blank=True)
    background_channel = models.IntegerField(choices=chan.items(), default=0)
    signal_channel = models.IntegerField(choices=chan.items(), default=0)
    ac1_channel = models.IntegerField(choices=chan.items(), default=0)
    aligned_bg = models.TextField(max_length=1000, blank=True)
    aligned_sg = models.TextField(max_length=1000, blank=True)
    aligned_ac1 = models.TextField(max_length=1000, blank=True)
    aligned_slice_score = models.CharField(max_length=20, blank=True)
    aligned_avgslice_score = models.CharField(max_length=20, blank=True)
    aligned_tif = models.TextField(max_length=1000, blank=True)
    user = models.ForeignKey(User, blank=False, default=0)
    def __str__(self):
        return self.name
    def complete(self):
        return 1000 > self.alignment_stage > 6
    complete.admin_order_field = 'name'
    complete.boolean = True
    complete.short_description = 'Alignment complete?'
    def curStage(self):
        return stage[self.alignment_stage]
    curStage.short_description = 'Current stage?'

class Original_nrrd(models.Model):
    image = models.ForeignKey(Alignment)
    channel = models.IntegerField(default=0)
    new_min = models.IntegerField(default=0)
    new_max = models.IntegerField(default=255)
    file = models.TextField(max_length=1000, blank=True)
    is_index = models.BooleanField(default=False)
    pre_hist = models.CommaSeparatedIntegerField(max_length=255, default=range(0,255))
    def __str__(self):
        return self.Alignment.name + ' channel ' + str(channel)

class Upload(models.Model):
    import system.models
    #from users.models import User
    #from system.models import Server, Setting, tempfolder
    file = models.FileField(upload_to='web' + os.path.sep)
    settings = models.ForeignKey('system.Setting', default=1)
    orientation = models.CharField(max_length=50, choices=orien, default='left-posterior-superior', blank=True)
    def curStage(self):
        return self.file
