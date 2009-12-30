from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.ForeignKey(User)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    path = models.CharField(max_length=36)

    name = models.CharField(max_length=50)

    arch = models.CharField(max_length=10, choices=settings.GEROBAK_ARCHS)

    repo = models.TextField(blank=True)
    repo_updated = models.DateTimeField(null=True)

    status_hash = models.CharField(max_length=40)
    status_updated = models.DateTimeField()

