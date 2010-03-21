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

@task(max_retries=1)
def search(id, packages):
    profile = Profile.objects.get(pk=id)

    path = utils.get_path(profile.pid)
    pkgs, ret, out, err = apt.search(path, packages)

    return pkgs, ret, out, err

@task(max_retries=1)
def upgrade(id):
    profile = Profile.objects.get(pk=id)

    path = utils.get_path(profile.pid)
    ret, out, err = apt.upgrade(path)

    return ret, out, err

@task(max_retries=1)
def dist_upgrade(id):
    profile = Profile.objects.get(pk=id)

    path = utils.get_path(profile.pid)
    ret, out, err = apt.dist_upgrade(path)

    return ret, out, err

