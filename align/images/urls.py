from django.conf.urls import url

from images import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^details/(?P<image_id>\w+)', views.detail, name='details'),
    url(r'^hist/(?P<image_id>\w+)', views.plotResults, name='histograms'),
    url(r'^nrrd/(?P<image_type>\w+)/(?P<image_id>\w+)', views.plotNrrd, name='nrrd'),
    # url(r'^/(?P<image_id>\w+/$)', views.detail, name='detail')
    # url(r'^$', views.index, name='details')
    # url(r'^/staticImage.png$', 'images.views.showStaticImage'),
    # url(r'^hist/$', views.index, name='index'),

]
