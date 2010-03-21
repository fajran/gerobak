from datetime import datetime

from celery.decorators import task

from gerobak.apps.profile.models import Profile
from gerobak import utils, apt

@task(max_retries=1)
def update(id):
    profile = Profile.objects.get(pk=id)

    path = utils.get_path(profile.pid)
    ret, out, err = apt.update(path)

    profile.repo_updated = datetime.now()
    profile.tid_update = None
    profile.save()

@task(max_retries=1)
def install(id, packages):
    profile = Profile.objects.get(pk=id)

    path = utils.get_path(profile.pid)
    pkgs, ret, out, err = apt.install(path, packages)

    return pkgs, ret, out, err

