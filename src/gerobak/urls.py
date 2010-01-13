from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

import gerobak.apps.profile.urls
#import gerobak.apps.queue

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),

    (r'^admin/', include(admin.site.urls)),

    (r'^doc/howto/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'doc/howto.html'}),

    (r'^p/', include(gerobak.apps.profile.urls)),
    #(r'^q/', include(gerobak.apps.queue.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^$', 'gerobak.views.index'),
)
