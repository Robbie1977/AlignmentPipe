from django.contrib import admin
from images.models import Alignment

class AlignmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'alignment_stage', 'max_stage']}),
        ('Original file details', {'fields': ['orig_orientation',
                              'original_path',
                              'original_ext',
                              'background_channel',
                              'signal_channel',
                              'AC1_channel'],
                              'classes': ['collapse']}),
        ('Alignment file details', {'fields': [ 'original_nrrd',
                              'temp_initial_nrrd',
                              'aligned_BG',
                              'aligned_SG',
                              'aligned_AC1'],
                              'classes': ['collapse']}),
        ('Alignment scores', {'fields': ['temp_initial_score',
                              'aligned_slice_score',
                              'aligned_avgSlice_score',
                              'aligned_score'],
                              'classes': ['collapse']}),
    ]
    list_display = ('name', 'complete', 'curStage')
    list_filter = ['alignment_stage']

admin.site.register(Alignment, AlignmentAdmin)
