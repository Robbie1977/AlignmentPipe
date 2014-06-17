from django.db import models
from socket import gethostname

host = gethostname()

stage = {0: 'failed (check settings and restart)',1:'preprocessing', 2:'initial alignment', 3:'affine alignment', 4:'final warp alignment', 5:'checking alignment', 6: 'aligning other channels', 7: 'alignment done'}
comp = {0: 'awaiting processing',1:'convertion complete', 2:'preprocessing complete', 3:'initial alignment complete', 4:'affine alignment complete', 5:'final warp complete', 6: 'background alignment complete', 7: 'all channels aligned'}
chan = {0: 'to be calculated', 1:'Channel 1', 2:'Channel 2', 3:'Channel 3'}
ori = ['LPS','RPI','RAS','LAI','PLI','PRS','ALS','ARI'] #X(>),Y(\/),Z(X).
orien = [str(x).replace('R','right-').replace('L','left-').replace('P','posterior-').replace('A','anterior-').replace('S','superior').replace('I','inferior') for x in ori]
comp_orien = dict(zip(ori,orien))
orien = zip(orien,orien)
conv_orien = dict(zip(comp_orien.values(),comp_orien.keys()))
# Create your models here.

class Alignment(models.Model):
    from system.models import Setting
    name = models.CharField(max_length=500)
    settings = models.ForeignKey(Setting, default=1)
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
    background_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
    signal_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
    ac1_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
    aligned_bg = models.TextField(max_length=1000, blank=True)
    aligned_sg = models.TextField(max_length=1000, blank=True)
    aligned_ac1 = models.TextField(max_length=1000, blank=True)
    aligned_slice_score = models.CharField(max_length=20, blank=True)
    aligned_avgslice_score = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.name
    def complete(self):
        return self.alignment_stage > 6
    complete.admin_order_field = 'name'
    complete.boolean = True
    complete.short_description = 'Alignment complete?'
    def curStage(self):
        return stage[self.alignment_stage]
    curStage.short_description = 'Current stage?'

class Original_nrrd(models.Model):
    image = models.ForeignKey(Alignment)
    channel = models.IntegerField(blank=True)
    new_min = models.IntegerField(blank=True)
    new_max = models.IntegerField(blank=True)
    file = models.TextField(max_length=1000, blank=True)
    is_index = models.BooleanField(default=False)
    pre_hist = models.CommaSeparatedIntegerField(max_length=255, blank=True)
    def __str__(self):
        return self.Alignment.name + ' channel ' + str(channel)

# class Choice(models.Model):
    # question = models.ForeignKey(Question)
    # choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)
