from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save

from gerobak import utils

class Profile(models.Model):
    user = models.ForeignKey(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=250, null=True, blank=True)

    arch = models.CharField(max_length=10, choices=settings.GEROBAK_ARCHS,
                            default=settings.GEROBAK_DEFAULT_ARCH)

    repo_updated = models.DateTimeField(null=True, default=None)
    sources_updated = models.DateTimeField(null=True, default=None)
    status_updated = models.DateTimeField(null=True, default=None)

    def is_ready(self):
        return self.repo_updated is not None and \
               self.status_updated is not None

