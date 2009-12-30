from django.conf.urls.defaults import *
from django.conf import settings

from gerobak.apps.profile import views

urlpatterns = patterns('',
    (r'^(?P<pid>\d+)/install/', views.install),
    (r'^(?P<pid>\d+)/search/', views.search),
    (r'^(?P<pid>\d+)/update/', views.update),
    (r'^(?P<pid>\d+)/sources/', views.sources),
    (r'^(?P<pid>\d+)/status/', views.status),
    #(r'^(?P<pid>\d+)/sources/', include(gerobak.apps.source.urls)),
    (r'^(?P<pid>\d+)/', views.show),
    (r'^$', views.index),
)
