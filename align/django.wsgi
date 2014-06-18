import os
import sys

sys.path.append('/disk/data/VFBTools/AlignmentPipe/align')
sys.path.append('/disk/data/VFBTools/AlignmentPipe/align/align')

os.environ['PYTHON_EGG_CACHE'] = '/disk/data/VFBTools/AlignmentPipe/align/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'align.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
