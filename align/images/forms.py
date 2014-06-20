from django import forms
from images.models import orien

class UploadForm(forms.Form):
    from system.models import Setting
    file = forms.FileField(
        label='Select a LSM or TIF file',
        help_text='max. 2 Gigabytes'
    )
    orientation = forms.ChoiceField(
        choices = orien,
        label='Select image orientation',
        initial = 'left-posterior-superior'
    )
    settings = forms.ModelChoiceField(
        queryset=Setting._default_manager,
        label='Select settings to use',
        empty_label=None
    )
