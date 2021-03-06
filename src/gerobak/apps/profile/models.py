from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save

from gerobak import utils

class Profile(models.Model):
    pid = models.CharField(max_length=8)

    user = models.ForeignKey(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=250, null=True, blank=True)

    arch = models.CharField(max_length=10, choices=settings.GEROBAK_ARCHS,
                            default=settings.GEROBAK_DEFAULT_ARCH)

    repo_updated = models.DateTimeField(null=True, default=None)

    sources_updated = models.DateTimeField(null=True, default=None)
    sources_total = models.IntegerField(null=True, default=None)

    status_updated = models.DateTimeField(null=True, default=None)
    status_hash = models.CharField(max_length=32, null=True, default=None)
    status_size = models.IntegerField(default=0)

    tid_update = models.CharField(max_length=36, null=True, default=None)

    def is_ready(self):
        return self.repo_updated is not None and \
               self.status_updated is not None

    def generate_pid(self):
        import uuid
        return str(uuid.uuid4()).split('-')[0]

