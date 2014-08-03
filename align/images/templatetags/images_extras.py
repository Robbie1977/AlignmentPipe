from django import template
from images.models import stage, chan, comp

register = template.Library()

@register.filter(name='state')
def state(value):
    return stage[value]

@register.filter(name='fini')
def fini(value):
    return comp[value]

@register.filter(name='channel')
def channel(value):
    return chan[value]

# @register.filter(name='joinby')
# def joinby(value, arg):
#     # if value is None:
#     #   return 'None'
#     # else:
#     #   return arg.join(value)
#     return 'Test'
