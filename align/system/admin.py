from django.contrib import admin
from django import forms
from system.models import Setting, Server, Template
from images.models import stage
import system.forms

serstage = stage.copy()
serstage[0] = 'edit original images'
serstage[7] = 'edit aligned images'
for i in serstage.keys():
  if int(i) > 8:
    serstage.pop(i, None)

STAGE_CHOICES = serstage.items()

class ServerForm(forms.ModelForm):
    run_stages = system.forms.CSIMultipleChoiceField(choices=STAGE_CHOICES)

class ServerAdmin(admin.ModelAdmin):
    form = ServerForm
    list_filter = ('active', )

class TemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('temp_image', )
TemplateAdmin.allow_tags = True

admin.site.register(Setting)
admin.site.register(Server, ServerAdmin)
admin.site.register(Template, TemplateAdmin)
