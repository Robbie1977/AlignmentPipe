from django.db import models

stage = {0: 'failed (check settings and restart)',1:'preprocessing', 2:'initial alignment', 3:'affine alignment', 4:'final warp alignment', 5:'checking alignment', 6: 'aligning other channels', 7: 'alignment done'}
chan = {0: 'to be calculated', 1:'Channel 1', 2:'Channel 2', 3:'Channel 3'}
ori = ['LPS','RPI','RAS','LAI','PLI','PRS','ALS','ARI'] #X(>),Y(\/),Z(X).
orien = [str(x).replace('R','right-').replace('L','left-').replace('P','posterior-').replace('A','anterior-').replace('S','superior').replace('I','inferior') for x in ori]
orien = zip(orien,orien)
# Create your models here.

class Alignment(models.Model):
    name = models.CharField(max_length=500)
    alignment_stage = models.IntegerField(choices=stage.items(), default=1)
    original_ext = models.CharField(max_length=10)
    original_path = models.TextField(max_length=1000)
    orig_orientation = models.CharField(max_length=50, choices=orien, default='left-posterior-superior', blank=True)
    temp_initial_nrrd = models.TextField(max_length=1000, blank=True)
    aligned_SG = models.TextField(max_length=1000, blank=True)
    original_nrrd = models.TextField(blank=True)
    temp_initial_score = models.CharField(max_length=20, blank=True)
    aligned_slice_score = models.CharField(max_length=20, blank=True)
    aligned_score = models.CharField(max_length=20, blank=True)
    aligned_avgSlice_score = models.CharField(max_length=20, blank=True)
    aligned_AC1 = models.TextField(max_length=1000, blank=True)
    AC1_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
    aligned_BG = models.TextField(max_length=1000, blank=True)
    background_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
    signal_channel = models.IntegerField(choices=chan.items(), default=0, blank=True)
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

# class Choice(models.Model):
    # question = models.ForeignKey(Question)
    # choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)
