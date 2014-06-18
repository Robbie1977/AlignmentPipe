from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'polls.views', name='views'),
    # url(r'^$', 'users.views.home'),
    url(r'^$', 'users.views.home', name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
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
)
