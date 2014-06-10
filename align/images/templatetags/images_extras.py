from django import template
from images.models import stage, chan

register = template.Library()

@register.filter(name='state')
def state(value):
    return stage[value]

@register.filter(name='channel')
def channel(value):
    return chan[value]
