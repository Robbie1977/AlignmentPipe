from django.contrib import admin
from images.models import Alignment, Original_nrrd
from system.models import Setting
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class CompleteStage(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Complete')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'complete'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('complete', _('alignment complete')),
            ('awaiting', _('awaiting an alignment stage')),
            ('processing', _('alignment stage in progress')),
            ('failed', _('awaiting user action')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'complete':
            return queryset.filter(alignment_stage__gte=7,
                                    alignment_stage__lte=999)
        if self.value() == 'awaiting':
            return queryset.filter(alignment_stage__gte=1,
                                    alignment_stage__lte=6)
        if self.value() == 'processing':
            return queryset.filter(alignment_stage__gte=1001,
                                    alignment_stage__lte=1999)
        if self.value() == 'failed':
            return queryset.filter(alignment_stage__lte=0)


class AlignmentAdmin(admin.ModelAdmin):
    exclude = ('aligned_tif')

    readonly_fields = ('max_stage',
                  'aligned_score',
                  'temp_initial_score',
                  'hist_image',
                  'ch1_image',
                  'ch2_image',
                  'ch3_image',
                  'init_image',
                  'temp_image',
                  'bg_image',
                  'sg_image',
                  'ac1_image',
                  'original_path',
                  'name',
                  'original_ext',
                  'temp_initial_nrrd',
                  'aligned_bg',
                  'aligned_sg',
                  'aligned_ac1',
                  'aligned_slice_score',
                  'aligned_avgslice_score',
                  'last_host',
                  'loading_host', )
    # fieldsets = [
    #     (None,               {'fields': ['name', 'settings', 'alignment_stage', 'max_stage']}),
    #     ('Original file details', {'fields': ['orig_orientation',
    #                           'original_path',
    #                           'original_ext',
    #                           'background_channel',
    #                           'signal_channel',
    #                           'ac1_channel'],
    #                           'classes': ['collapse']}),
    #     ('Alignment file details', {'fields': [ 'original_nrrd',
    #                           'temp_initial_nrrd',
    #                           'aligned_bg',
    #                           'aligned_sg',
    #                           'aligned_ac1'],
    #                           'classes': ['collapse']}),
    #     ('Alignment scores', {'fields': ['temp_initial_score',
    #                           'aligned_slice_score',
    #                           'aligned_avgSlice_score',
    #                           'aligned_score'],
    #                           'classes': ['collapse']}),
    # ]
    list_display = ('name', 'user', 'complete', 'curStage', 'temp_initial_score', 'aligned_score') #, 'last_host'
    list_filter = ['alignment_stage', 'user', CompleteStage] #'last_host',

    def queryset(self, request):
      if request.user.is_superuser:
        return Alignment.objects.all()
      return Alignment.objects.filter(Q(user=request.user) | Q(user=0))

AlignmentAdmin.allow_tags = True
admin.site.register(Alignment, AlignmentAdmin)
