from django.contrib import admin
from django import forms
from system.models import Setting, Server, Template
from images.models import stage
import system.forms

STAGE_CHOICES = stage.items()[1:-1]

class ServerForm(forms.ModelForm):
    run_stages = system.forms.CSIMultipleChoiceField(choices=STAGE_CHOICES)

class ServerAdmin(admin.ModelAdmin):
    form = ServerForm


admin.site.register(Setting)
admin.site.register(Server, ServerAdmin)
admin.site.register(Template)
