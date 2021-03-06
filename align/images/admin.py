from django.contrib import admin
from images.models import Alignment, Original_nrrd, Mask_aligned, Mask_original
from system.models import Setting
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django import forms
import system.forms


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
            ('paused', _('paused during alignment process')),
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
        if self.value() == 'paused':
            return queryset.filter(alignment_stage__gte=2000,
                                    alignment_stage__lte=2999)
        if self.value() == 'failed':
            return queryset.filter(alignment_stage__lte=0)

class AvailableUsers(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('User')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'users'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (('public', _('public alignments')),
                ('me', _('your alignments')))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'public':
            return queryset.filter(user=0)
        if self.value() == 'me':
            return queryset.filter(user=request.user)


class OriginalMaskAdminInline(admin.StackedInline):
    model = Mask_original

class AlignedMaskAdminInline(admin.StackedInline):
    model = Mask_aligned

class OriginalAdminInline(admin.StackedInline):
    model = Original_nrrd


class AlignmentAdmin(admin.ModelAdmin):
    exclude = ('aligned_tif')

    readonly_fields = ('max_stage',
                  'aligned_score',
                  'temp_initial_score',
                  'hist_image',
                  # 'ch1_image',
                  # 'ch2_image',
                  # 'ch3_image',
                  'init_image',
                  'temp_image',
                  'bg_image',
                  'bg_download',
                  'sg_image',
                  'sg_download',
                  'ac1_image',
                  'ac1_download',
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
    list_display = ('name', 'user', 'complete', 'curStage', 'max_stage', 'temp_initial_score', 'aligned_score', 'notes') #, 'last_host'
    list_filter = [AvailableUsers, CompleteStage, 'alignment_stage', 'max_stage'] #'last_host',
    # inlines = [OriginalAdminInline, AlignedMaskAdminInline]

    def queryset(self, request):
      if request.user.is_superuser:
        return Alignment.objects.all()
      return Alignment.objects.filter(Q(user=request.user) | Q(user=0))
    def show_ch1_image(self, obj):
      im_id = Original_nrrd.object.filter(image=obj.id).filter(channel=1)
      return '<a href="/admin/images/mask_original/add/?image=%s">Create ch1 mask</a>' % (im_id.pk)
    show_ch1_image.allow_tags = True

AlignmentAdmin.allow_tags = True
admin.site.register(Alignment, AlignmentAdmin)

class OriginalAdmin(admin.ModelAdmin):
    readonly_fields = ('image',
                    'channel',
                    'chan_ident',
                    'chan_image',
                    'chan_download',
                    'new_min',
                    'new_max',
                    'file',
                    'is_index',
                    'pre_hist',
                    'parent' )
    list_display = ('image',
                    'chan_ident',
                    'channel',
                    'new_min',
                    'new_max',
                    'owner' )
    list_filter = ['channel', 'is_index']
    # inlines = (OriginalMaskAdminInline, )
    # def queryset(self, request):
    #   if request.user.is_superuser:
    #     return Original_nrrd.objects.all()
    #   return Original_nrrd.objects.filter(Q(alignment__user=request.user) | Q(alignment__user=0))
    def queryset(self, request):
      if request.user.is_superuser:
        return Original_nrrd.objects.all()
      return Original_nrrd.objects.filter(image__user__in=[request.user, 0])
OriginalAdmin.allow_tags = True
admin.site.register(Original_nrrd, OriginalAdmin)



class MaskForm(forms.ModelForm):
    cut_objects = system.forms.CSIMultipleChoiceField(choices=((1, 'object labeled 1'), (2, 'object labeled 2'), (3, 'object labeled 3'), (4, 'object labeled 4'), (5, 'object labeled 5'), (6, 'object labeled 6'), (7, 'object labeled 7'), (8, 'object labeled 8'), (9, 'object labeled 9'), (0, 'background')))
    cut_objects.required = False
    crop_objects = system.forms.CSIMultipleChoiceField(choices=((1, 'object labeled 1'), (2, 'object labeled 2'), (3, 'object labeled 3'), (4, 'object labeled 4'), (5, 'object labeled 5'), (6, 'object labeled 6'), (7, 'object labeled 7'), (8, 'object labeled 8'), (9, 'object labeled 9'), (0, 'background')))
    crop_objects.required = False

class MaskAlignedAdmin(admin.ModelAdmin):
    form = MaskForm
    # exclude = ('image')
    readonly_fields = ('available', 'mask_image', 'detected_objects', 'mask_download', 'orig_image', 'image_download', 'mod_image', 'modified_download', 'owner', 'parent', )
    list_display = ('image', 'available', 'complete', 'detected_objects', 'cut_complete', 'crop_complete', 'owner', 'notes', )
    list_filter = ('channel', 'complete', 'cut_complete', 'crop_complete', )
    def queryset(self, request):
      if request.user.is_superuser:
        return Mask_aligned.objects.all()
      return Mask_aligned.objects.filter(image__user__in=[request.user, 0]).filter(image__alignment_stage=7)
MaskAlignedAdmin.allow_tags = True
admin.site.register(Mask_aligned, MaskAlignedAdmin)

class MaskOriginalAdmin(admin.ModelAdmin):
    form = MaskForm
    # exclude = ('image')
    readonly_fields = ('available', 'mask_image', 'detected_objects', 'mask_download', 'orig_image', 'image_download', 'mod_image', 'modified_download', 'owner', 'parent', )
    list_display = ('image', 'available', 'chan_ident', 'complete', 'detected_objects', 'cut_complete', 'crop_complete', 'auto_restart_alignment', 'owner', 'notes', )
    list_filter = ('complete', 'cut_complete', 'crop_complete', 'overwrite_original', 'auto_restart_alignment', )
    def queryset(self, request):
      if request.user.is_superuser:
        return Mask_original.objects.all()
      return Mask_original.objects.filter(image__image__user__in=[request.user, 0]).filter(image__image__alignment_stage=0)
MaskOriginalAdmin.allow_tags = True
admin.site.register(Mask_original, MaskOriginalAdmin)
