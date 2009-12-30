from datetime import datetime
import os
import shutil
import hashlib
import subprocess
import re

from django.conf import settings

def init(profile):
    src = os.path.join(settings.GEROBAK_PROFILE_DIR, 'base')
    target = os.path.join(settings.GEROBAK_PROFILE_DIR, profile.path)
    shutil.copytree(src, target)

    f = open(os.path.join(target, "apt.conf"), "a")
    f.write('APT::Architecture "%s";\n' % profile.arch)
    f.close()

    sources_list = os.path.join(target, 'sources.list')
    content = open(sources_list).read()

    sha1 = hashlib.sha1()
    sha1.update(content)
    sha1.digest()

    profile.repo = content
    profile.repo_updated = datetime.now()
    profile.status_hash = sha1.hexdigest()
    profile.status_update = None

    profile.save()

def _apt(target, cmd, *args):
    conf = os.path.join(target, 'apt.conf')

    param = [cmd, '-c', conf, 'update']
    param += args

    sp = subprocess.Popen(args, cwd=target, 
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)

    return sp

def _apt_get(target, *args):
    return _apt(target, settings.GEROBAK_APT_GET, *args)

def _apt_cache(target, *args):
    return _apt(target, settings.GEROBAK_APT_CACHE, *args)

_re_pkg = re.compile(r'/^[a-z0-9][a-z0-9.-]*/')

def _package_filter(pkg):
    return _re_pkg.match(pkg)

def _clean_packages(packages):
    return filter(_package_filter, packages.split())

def update(profile):
    target = os.path.join(settings.GEROBAK_PROFILE_DIR, profile.path)
    sp = _apt_get(target, 'update')
    sp.wait()

    if sp.returncode == 0:
        profile.status_update = datetime.now()
        profile.save()

    return (sp.returncode, sp.stdout.read(), sp.stderr.read())

def upgrade(profile):
    target = os.path.join(settings.GEROBAK_PROFILE_DIR, profile.path)
    sp = _apt_get(target, 'upgrade')
    sp.wait()

    return (sp.returncode, sp.stdout.read(), sp.stderr.read())

def install(profile, packages):
    pkgs = _clean_packages(packages)
    target = os.path.join(settings.GEROBAK_PROFILE_DIR, profile.path)
    sp = _apt_get(target, 'install', '--print-uris', '-y', *pkgs)
    sp.wait()

    return (pkgs, sp.returncode, sp.stdout.read(), sp.stderr.read())

def search(profile, packages):
    pkgs = _clean_packages(packages)
    target = os.path.join(settings.GEROBAK_PROFILE_DIR, profile.path)
    sp = _apt_cache(target, 'search', *pkgs)
    sp.wait()

    return (pkgs, sp.returncode, sp.stdout.read(), sp.stderr.read())

