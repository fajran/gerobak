from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

import gerobak.apps.profile
import gerobak.apps.queue

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),

    (r'^admin/', include(admin.site.urls)),

    (r'^p/', include(gerobak.apps.profile.urls)),
    (r'^q/', include(gerobak.apps.queue.urls)),
    (r'^$', 'gerobak.views.index'),
)
