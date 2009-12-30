from datetime import datetime
import os
import shutil
import hashlib
import subprocess
import re

from django.conf import settings

def _apt(path, cmd, *args):
    conf = os.path.join(path, 'apt.conf')

    param = [cmd, '-c', conf]
    param += args
    print param

    sp = subprocess.Popen(param, cwd=path, 
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)

    return sp

def _apt_get(path, *args):
    return _apt(path, settings.GEROBAK_APT_GET, *args)

def _apt_cache(path, *args):
    return _apt(path, settings.GEROBAK_APT_CACHE, *args)

_re_pkg = re.compile(r'^[a-z0-9][a-z0-9.-]*$')
def _package_filter(pkg):
    return _re_pkg.match(pkg)

def _clean_packages(packages):
    return filter(_package_filter, packages.split())

def update(path):
    sp = _apt_get(path, 'update')
    sp.wait()

    return sp.returncode, sp.stdout.read(), sp.stderr.read()

def upgrade(path):
    sp = _apt_get(path, 'upgrade')
    sp.wait()

    return sp.returncode, sp.stdout.read(), sp.stderr.read()

def install(path, packages):
    pkgs = _clean_packages(packages)
    sp = _apt_get(path, 'install', '--print-uris', '-y', *pkgs)
    sp.wait()

    return pkgs, sp.returncode, sp.stdout.read(), sp.stderr.read()

def search(path, packages):
    pkgs = _clean_packages(packages)
    sp = _apt_cache(path, 'search', *pkgs)
    sp.wait()

    return pkgs, sp.returncode, sp.stdout.read(), sp.stderr.read()

