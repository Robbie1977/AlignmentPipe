from django.db import models
from socket import gethostname
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
import os

host = gethostname()

stage = {0: 'failed (check settings and restart)',1:'preprocessing', 1001:'preprocessing image stack', 2:'initial alignment', 1002:'calculating initial alignment', 3:'affine alignment', 1003:'processing affine alignment', 4:'final warp alignment', 1004:'processing warp alignment', 5:'checking alignment', 1005:'aligning BG channel', 6: 'aligning other channels', 1006:'aligning all channel using BG warp', 7: 'alignment done', 10:'request merged tif',  1010:'creating merged tif', 20:'merged tif created'}
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
    crop_xyz = models.CharField(max_length=100, blank=True)
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
    notes = models.TextField(max_length=10000, blank=True)
    reference = models.TextField(max_length=5000, blank=True)
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
    def ch1_image(self):
      if self.max_stage > 1:
        return '<img src="/images/nrrd/Ch1_file/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    ch1_image.short_description = 'original image ch1'
    ch1_image.allow_tags = True
    def ch2_image(self):
      if self.max_stage > 1:
        return '<img src="/images/nrrd/Ch2_file/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    ch2_image.short_description = 'original image ch2'
    ch2_image.allow_tags = True
    def ch3_image(self):
      if self.max_stage > 1:
        return '<img src="/images/nrrd/Ch3_file/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    ch3_image.short_description = 'original image ch3'
    ch3_image.allow_tags = True
    def bg_image(self):
      if self.max_stage > 5:
        return '<img src="/images/nrrd/aligned_bg/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    bg_image.short_description = 'aligned BG image'
    bg_image.allow_tags = True
    def sg_image(self):
      if self.max_stage > 6:
        return '<img src="/images/nrrd/aligned_sg/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    sg_image.short_description = 'aligned SG image'
    sg_image.allow_tags = True
    def ac1_image(self):
      if self.max_stage > 6:
        return '<img src="/images/nrrd/aligned_ac1/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    ac1_image.short_description = 'aligned AC1 image'
    ac1_image.allow_tags = True
    def hist_image(self):
      if self.max_stage > 1:
        return '<img src="/images/hist/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    hist_image.short_description = 'original image histogram (new contrast range maked in cyan)'
    hist_image.allow_tags = True
    def init_image(self):
      if self.max_stage > 2:
        return '<img src="/images/nrrd/temp_initial_nrrd/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    init_image.short_description = 'initial BG alignment'
    init_image.allow_tags = True
    def temp_image(self):
        return '<img src="/images/nrrd/template/%s"/>' % str(self.id)
    temp_image.short_description = 'template image for reference'
    temp_image.allow_tags = True
    # def available_files(self):
    #     created = {}
    #     if 'nrrd' in self.aligned_bg:
    #       created.append({'Aligned BG':str(self.aligned_bg)})
    #     if 'nrrd' in self.aligned_sg:
    #       created.append({'Aligned SG':str(self.aligned_sg)})
    #     if 'nrrd' in self.aligned_ac1:
    #       created.append({'Aligned AC1':str(self.aligned_ac1)})
    #     return created


class Original_nrrd(models.Model):
    image = models.ForeignKey(Alignment)
    channel = models.IntegerField(default=0)
    new_min = models.IntegerField(default=0)
    new_max = models.IntegerField(default=255)
    file = models.TextField(max_length=1000, blank=True)
    is_index = models.BooleanField(default=False)
    pre_hist = models.CommaSeparatedIntegerField(max_length=255, default=range(0,255))
    def __str__(self):
        return str(self.image) + ' channel ' + str(self.channel)
    def owner(self):
        im_id = self.image
        return str(im_id.user)
    owner.admin_order_field = 'image'
    owner.short_description = 'User'
    # def available_files(self):
    #   created = {}
    #   if 'nrrd' in str(self.file):
    #     created.append({('Original Ch' + str(self.channel)):str(self.file)})
    #   return created

class Upload(models.Model):
    import system.models
    #from users.models import User
    #from system.models import Server, Setting, tempfolder
    file = models.FileField(upload_to='web' + os.path.sep)
    settings = models.ForeignKey('system.Setting', default=1)
    orientation = models.CharField(max_length=50, choices=orien, default='left-posterior-superior', blank=True)
    def curStage(self):
        return self.file

class Mask_original(models.Model):
    image = models.ForeignKey(Original_nrrd)
    intensity_threshold = models.IntegerField(default=20)
    min_object_size = models.IntegerField(default=1000)
    complete = models.BooleanField(default=False)
    def __str__(self):
        return 'Mask for ' + str(self.image)

class Mask_aligned(models.Model):
    image = models.ForeignKey(Alignment)
    channel = models.CharField(max_length=3, choices=(('bg', 'Background'),('sg', 'Signal'),('ac1', 'Additional')), default='sg')
    intensity_threshold = models.IntegerField(default=20)
    min_object_size = models.IntegerField(default=1000)
    complete = models.BooleanField(default=False)
    def __str__(self):
        return 'Mask for aligned ' + str(self.image) + ' ' + str(self.channel).upper() + ' channel'
