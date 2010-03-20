from django.conf.urls.defaults import *
from django.conf import settings

from gerobak.apps.profile import views

urlpatterns = patterns('',
    (r'^(?P<pid>[a-f0-9]{8})/install/$', views.install),
    (r'^(?P<pid>[a-f0-9]{8})/upgrade/$', views.upgrade),
    (r'^(?P<pid>[a-f0-9]{8})/dist-upgrade/$', views.dist_upgrade),
    (r'^(?P<pid>[a-f0-9]{8})/search/$', views.search),
    (r'^(?P<pid>[a-f0-9]{8})/update/$', views.update),
    (r'^(?P<pid>[a-f0-9]{8})/sources/$', views.sources),
    (r'^(?P<pid>[a-f0-9]{8})/status/$', views.status),
    (r'^(?P<pid>[a-f0-9]{8})/show/(?P<pkg>[a-z0-9.-]+)/$', views.info),
    #(r'^(?P<pid>\d+)/sources/', include(gerobak.apps.source.urls)),
    (r'^(?P<pid>[a-f0-9]{8})/$', views.show),
    (r'^$', views.index),
)
