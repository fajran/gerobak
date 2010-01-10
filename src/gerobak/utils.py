import uuid
import shutil
import os
import hashlib

from django.conf import settings

#from gerobak.models import Profile
from gerobak import apt

def get_path(pid):
    return os.path.join(os.path.abspath(settings.GEROBAK_WORKING_DIR), 
                        str(pid))

def prepare_profile_dir(path):
    src = os.path.join(settings.GEROBAK_WORKING_DIR, 'base')
    shutil.copytree(src, path)

def configure_profile(path, **config):
    # architecture
    arch = config.get('arch', settings.GEROBAK_DEFAULT_ARCH)
    f = open(os.path.join(path, "apt.conf"), "a")
    f.write('APT::Architecture "%s";\n' % arch)
    f.close()

def get_repo(path):
    f = open(os.path.join(path, 'sources.list'))
    content = f.read()
    f.close()
    return content
    
def update_status(path, status):
    shutil.copyfile(status, os.path.join(path, 'status'))

def get_status_info(path):
    status = os.path.join(path, 'status')

    m = hashlib.md5()
    m.update(open(status).read())
    m.digest()
    hash = m.hexdigest()

    size = os.path.getsize(status)

    return size, hash

def update_sources(path, items):
    sources = items
    if type(items) == sources:
        sources = "\n".join(items)

    f = open(os.path.join(path, 'sources.list'), 'w')
    f.write(sources)
    f.close()

