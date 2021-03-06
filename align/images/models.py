import os
from socket import gethostname

from django.contrib.auth.models import User
from django.db import models

host = gethostname()

stage = {0:'failed (check settings and restart)',1:'preprocessing', 1001:'preprocessing image stack', 2:'initial alignment', 1002:'calculating initial alignment', 3:'affine alignment', 1003:'processing affine alignment', 4:'final warp alignment', 1004:'processing warp alignment', 5:'checking alignment', 1005:'aligning BG channel', 6: 'aligning other channels', 1006:'aligning all channel using BG warp', 7:'alignment done', 10:'request merged tif', 11: 'show in VFB',  1010:'creating merged tif', 20:'merged tif created', 21: 'available in VFB', 2001:'paused before preprocessing', 2002:'paused before initial alignment', 2003:'paused before affine alignment', 2004:'paused before warp alignment', 2005:'paused before BG alignment', 2006:'paused before SG alignment' }
comp = {0:'awaiting processing',1:'convertion complete', 2:'preprocessing complete', 3:'initial alignment complete', 4:'affine alignment complete', 5:'final warp complete', 6: 'background alignment complete', 7: 'all channels aligned', 10: 'merged tif requested', 11: 'show in VFB', 20: 'merged tif created', 21: 'available in VFB'}
chan = {0: 'to be calculated', 1:'Channel 1', 2:'Channel 2', 3:'Channel 3'}
ori = ['LPS', 'RPI', 'RAS', 'RIA', 'RSP', 'LAI', 'LSA', 'LIP', 'PLI', 'PRS', 'PIR', 'PSL', 'ALS', 'ARI', 'ASR', 'AIL',
       'ILA', 'IRP', 'IAR', 'IPL', 'SPR', 'SRA', 'SAL', 'SLP']  # X(>),Y(\/),Z(X).
orien = [
    str(x[0] + '-' + x[1] + '-' + x[2]).replace('R', 'right').replace('L', 'left').replace('P', 'posterior').replace(
        'A', 'anterior').replace('S', 'superior').replace('I', 'inferior') for x in ori]
comp_orien = dict(zip(ori,orien))
orien = zip(orien,orien)
conv_orien = dict(zip(comp_orien.values(),comp_orien.keys()))
# Create your models here.

class Alignment(models.Model):
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
    def bg_download(self):
      return '<a href="/static/downloads/%s"/>%s</a>' % (str(self.aligned_bg), str(self.aligned_bg))
    bg_download.short_description = 'download aligned background'
    bg_download.allow_tags = True
    def sg_image(self):
      if self.max_stage > 6:
        return '<img src="/images/nrrd/aligned_sg/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    sg_image.short_description = 'aligned SG image'
    sg_image.allow_tags = True
    def sg_download(self):
      return '<a href="/static/downloads/%s"/>%s</a>' % (str(self.aligned_sg), str(self.aligned_sg))
    sg_download.short_description = 'download aligned signal'
    sg_download.allow_tags = True
    def ac1_image(self):
      if self.max_stage > 6:
        return '<img src="/images/nrrd/aligned_ac1/%s"/>' % str(self.id)
      return '<img src="/static/waiting.gif"/>'
    ac1_image.short_description = 'aligned AC1 image'
    ac1_image.allow_tags = True
    def ac1_download(self):
      return '<a href="/static/downloads/%s"/>%s</a>' % (str(self.aligned_ac1), str(self.aligned_ac1))
    ac1_download.short_description = 'download aligned additional channel 1'
    ac1_download.allow_tags = True
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
        return '<img src="%s"/>' % str(self.settings.template.image)
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
    def chan_image(self):
      return '<img src="/images/nrrd/Ch%s_file/%s"/>' % (str(self.channel), str(self.image.id))
    chan_image.short_description = 'channel image'
    chan_image.allow_tags = True
    def chan_download(self):
      return '<a href="/static/downloads/%s"/>%s</a>' % (str(self.file), str(self.file))
    chan_download.short_description = 'download original channel'
    chan_download.allow_tags = True
    def chan_ident(self):
      ident = '...'
      if str(self.channel) == str(self.image.background_channel):
        ident = 'background'
      if str(self.channel) == str(self.image.signal_channel):
        ident = 'signal'
      if str(self.channel) == str(self.image.ac1_channel):
        ident = 'additional channel 1'
      return ident
    chan_ident.short_description = 'channel identified as'
    def parent(self):
      return '<a href="/admin/images/alignment/%s"/>%s</a>' % (str(self.image.id), str(self.image))
    parent.short_description = 'parent details'
    parent.allow_tags = True

class Upload(models.Model):
    #from users.models import User
    #from system.models import Server, Setting, tempfolder
    file = models.FileField(upload_to='web' + os.path.sep)
    settings = models.ForeignKey('system.Setting', default=1)
    orientation = models.CharField(max_length=50, choices=orien, default='left-posterior-superior', blank=True)
    def curStage(self):
        return self.file

class Mask_original(models.Model):
    image = models.ForeignKey(Original_nrrd)
    intensity_threshold = models.IntegerField(default=35)
    min_object_size = models.IntegerField(default=10000)
    complete = models.BooleanField(default=False)
    detected_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    cut_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    cut_complete = models.BooleanField(default=False)
    crop_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    crop_complete = models.BooleanField(default=False)
    overwrite_original = models.BooleanField(default=False)
    auto_restart_alignment = models.BooleanField(default=False)
    notes = models.TextField(max_length=10000, blank=True)
    def __str__(self):
        return 'Mask for ' + str(self.image)
    def mask_image(self):
      if self.complete:
        return '<img src="/images/nrrd/mask_original/%s-%s"/>' % (str(self.image.id),str(self.id))
      return '<img src="/static/waiting.gif"/>'
    mask_image.short_description = 'detected objects'
    mask_image.allow_tags = True
    def orig_image(self):
      ch_id = self.image
      im_id = ch_id.image
      try:
        return '<img src="/images/nrrd/Ch%s_file/%s"/>' % (str(ch_id.channel), str(im_id.id))
      except:
        return '<img src="/static/waiting.gif"/>'
    orig_image.short_description = 'original image'
    orig_image.allow_tags = True
    def mod_image(self):
      try:
        return '<img src="/images/nrrd/mod_original/%s-%s"/>' % (str(self.image.id),str(self.id))
      except:
        return '<img src="/static/waiting.gif"/>'
    mod_image.short_description = 'modified image'
    mod_image.allow_tags = True
    def owner(self):
      ch_id = self.image
      im_id = ch_id.image
      return str(im_id.user)
    owner.admin_order_field = 'image'
    owner.short_description = 'User'
    def chan_ident(self):
      ident = '...'
      if str(self.image.channel) == str(self.image.image.background_channel):
        ident = 'background'
      if str(self.image.channel) == str(self.image.image.signal_channel):
        ident = 'signal'
      if str(self.image.channel) == str(self.image.image.ac1_channel):
        ident = 'additional channel 1'
      return ident
    chan_ident.short_description = 'channel identified as'
    def parent(self):
      return '<a href="/admin/images/alignment/%s"/>%s</a>' % (str(self.image.image.id), str(self.image.image))
    parent.short_description = 'parent details'
    parent.allow_tags = True
    def modified_download(self):
      chanFile = str(self.image.file).replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(self.id) + '.nrrd')
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    modified_download.short_description = 'download modified image'
    modified_download.allow_tags = True
    def image_download(self):
      chanFile = str(self.image.file)
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    image_download.short_description = 'download image'
    image_download.allow_tags = True
    def mask_download(self):
      chanFile = str(self.image.file)
      chanFile = chanFile.replace('.nrrd','-objMask.nrrd').replace('.nrrd',str(self.id) + '.nrrd')
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    mask_download.short_description = 'download image mask'
    mask_download.allow_tags = True
    def available(self):
      try:
        if self.image.image.alignment_stage > 0:
          return False
        else:
          return True
      except:
        return False
    available.boolean = True
    available.short_description = 'available for manual processing'

class Mask_aligned(models.Model):
    image = models.ForeignKey(Alignment)
    channel = models.CharField(max_length=3, choices=(('bg', 'Background'),('sg', 'Signal'),('ac1', 'Additional')), default='sg')
    intensity_threshold = models.IntegerField(default=20)
    min_object_size = models.IntegerField(default=1000)
    complete = models.BooleanField(default=False)
    detected_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    cut_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    cut_complete = models.BooleanField(default=False)
    crop_objects = models.CommaSeparatedIntegerField(max_length=255, blank=True, default={})
    crop_complete = models.BooleanField(default=False)
    notes = models.TextField(max_length=10000, blank=True)
    def __str__(self):
        return 'Mask for aligned ' + str(self.image) + ' ' + str(self.channel).upper() + ' channel'
    def mask_image(self):
      if self.complete:
         return '<img src="/images/nrrd/mask_aligned_%s/%s-%s"/>' % (str(self.channel), str(self.image.id), str(self.id))
      return '<img src="/static/waiting.gif"/>'
    mask_image.short_description = 'detected objects'
    mask_image.allow_tags = True
    def orig_image(self):
      im_id = self.image
      try:
        return '<img src="/images/nrrd/aligned_%s/%s"/>' % (str(self.channel), str(im_id.id))
      except:
        return '<img src="/static/waiting.gif"/>'
    orig_image.short_description = 'original image'
    orig_image.allow_tags = True
    def mod_image(self):
      try:
        return '<img src="/images/nrrd/mod_aligned_%s/%s-%s"/>' % (str(self.channel), str(self.image.id),str(self.id))
      except:
        return '<img src="/static/waiting.gif"/>'
    mod_image.short_description = 'modified image'
    mod_image.allow_tags = True
    def owner(self):
      im_id = self.image
      return str(im_id.user)
    owner.admin_order_field = 'image'
    owner.short_description = 'User'
    def parent(self):
      return '<a href="/admin/images/alignment/%s"/>%s</a>' % (str(self.image.id), str(self.image))
    parent.short_description = 'parent details'
    parent.allow_tags = True
    def image_download(self):
      chanFile = str(self.image.aligned_sg)
      if str(self.channel) == 'bg':
        chanFile = self.image.aligned_bg
      if str(self.channel) == 'ac1':
        chanFile = self.image.aligned_ac1
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    image_download.short_description = 'download image'
    image_download.allow_tags = True
    def mask_download(self):
      chanFile = str(self.image.aligned_sg)
      if str(self.channel) == 'bg':
        chanFile = self.image.aligned_bg
      if str(self.channel) == 'ac1':
        chanFile = self.image.aligned_ac1
      chanFile = chanFile.replace('.nrrd','-objMask.nrrd').replace('.nrrd', str(self.id) + '.nrrd')
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    mask_download.short_description = 'download image mask'
    mask_download.allow_tags = True
    def modified_download(self):
      chanFile = str(self.image.aligned_sg)
      if str(self.channel) == 'bg':
        chanFile = self.image.aligned_bg
      if str(self.channel) == 'ac1':
        chanFile = self.image.aligned_ac1
      chanFile = chanFile.replace('.nrrd','-ModFile.nrrd').replace('.nrrd', str(self.id) + '.nrrd')
      return '<a href="/static/downloads/%s"/>%s</a>' % (chanFile, chanFile)
    modified_download.short_description = 'download modified image'
    modified_download.allow_tags = True
    def available(self):
      try:
        if self.image.alignment_stage < 1:
          return True
        if self.image.alignment_stage < 7:
          return False
        else:
          return True
      except:
        return False
    available.boolean = True
    available.short_description = 'available for manual processing'
