from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
actions.add_to_site(site)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'polls.views', name='views'),
    # url(r'^$', include(admin.site.urls)),
    url(r'^$', 'users.views.home', name='home'),
    url(r'^', include('social.apps.django_app.urls', namespace='social')),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    # url(r'^email-sent/', 'users.views.validation_sent'),
    # url(r'^login/$', 'users.views.home'),
    # url(r'^logout/$', 'users.views.logout'),
    # url(r'^done/$', 'users.views.done', name='done'),
    # url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'users.views.ajax_auth', name='ajax-auth'),
    # url(r'^email/$', 'users.views.require_email', name='require_email'),
    # url(r'', include('social.apps.django_app.urls', namespace='social')),
    # url(r'^$', include('images.urls')),
    url(r'^images/', include('images.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/$', 'images.views.upload', name='upload'),
    url(r'^adminactions/', include('adminactions.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
