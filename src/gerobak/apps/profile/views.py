from datetime import datetime
import tempfile
import os

try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django import forms
from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from celery.result import AsyncResult

from gerobak import utils, apt
from gerobak.apps.profile import tasks
from gerobak.apps.profile.models import Profile
from gerobak.apps.profile.utils import parse_apt_install, \
                                       parse_apt_search, \
                                       parse_apt_show

class AddProfileForm(forms.Form):
    name = forms.CharField(max_length=50)
    desc = forms.CharField(max_length=250, label="Description")
    arch = forms.ChoiceField(choices=settings.GEROBAK_ARCHS,
                             initial=settings.GEROBAK_DEFAULT_ARCH,
                             label="Architecture")

class UploadStatusForm(forms.Form):
    file = forms.FileField()

class SourcesForm(forms.Form):
    sources = forms.CharField(widget=forms.Textarea)

class InstallForm(forms.Form):
    packages = forms.CharField()

class SearchForm(forms.Form):
    packages = forms.CharField()

def _post(func):
    def _func(request, pid, *args, **kwargs):
        if request.method != 'POST':
            return redirect(show, pid)
        return func(request, pid, *args, **kwargs)
    return _func

def _profile(func):
    def _func(request, pid, *args, **kwargs):
        profile = get_object_or_404(Profile, pid=pid)
        if profile.user != request.user:
            # TODO
            return HttpResponseForbidden()
        return func(request, profile, *args, **kwargs)
    return _func

def _updated(func):
    def _func(request, profile, *args, **kwargs):
        if profile.status_updated is None or \
           profile.sources_updated is None or \
           profile.repo_updated is None:
            
            request.user.message_set.create(message="update needed.")
            return redirect(show, profile.pid)

        return func(request, profile, *args, **kwargs)
    return _func

def _pre_updated(func):
    def _func(request, profile, *args, **kwargs):
        if profile.status_updated is None or \
           profile.sources_updated is None:
            
            request.user.message_set.create(message="status or sources is missing")
            return redirect(show, profile.pid)

        return func(request, profile, *args, **kwargs)
    return _func

def _decompress(realname, path):
    # FIXME uncompressed file size should be checked and limited

    fid, tmp = tempfile.mkstemp()
    fo = open(tmp, 'w')

    if realname.endswith('.gz'):
        import gzip
        fi = gzip.open(path, 'rb')

    elif realname.endswith('.bz2'):
        import bz2
        fi = bz2.BZ2File(path, 'r')

    fo.write(fi.read())

    fi.close()
    fo.close()

    return tmp

def handle_uploaded_status(profile, file):
    # FIXME file size should be checked and limited

    path = utils.get_path(profile.pid)
    status = file.temporary_file_path()

    tmp = None
    if file.name.endswith('.gz') or file.name.endswith('.bz2'):
        tmp = _decompress(file.name, file.temporary_file_path())
        utils.update_status(path, tmp)
        os.unlink(tmp)

    else:
        utils.update_status(path, status)

    return path

def _upgrade(request, profile, type='upgrade'):
    task = tasks.upgrade.delay(profile.id, type)
    data = {'stat': 'ok',
            'task_id': task.task_id}

    return render_to_response('profile/json', {'json': json.dumps(data)},
                              mimetype='text/plain')

@login_required
@_post
@_profile
@_updated
def upgrade(request, profile):
    return _upgrade(request, profile)

@login_required
@_post
@_profile
@_updated
def dist_upgrade(request, profile):
    return _upgrade(request, profile, 'dist-upgrade')

@login_required
@_profile
@_updated
def upgrade_result(request, profile, task_id):
    task = AsyncResult(task_id)
    if task.status == 'SUCCESS':
        type, ret, out, err = task.result
        return _show_install(ret, out, err, 'json', type=type)
    elif task.status == 'PENDING':
        data = {'stat': 'pending'}
    else:
        data = {'stat': 'fail'}
    return render_to_response('profile/json', {'json': json.dumps(data)},
                              mimetype='text/plain')

def _show_install(ret, out, err, format, **kwargs):
    if ret != 0:
        txt = err
    else:
        txt = out

    extra, suggested, recommended, install, packages, newest, \
        upgrade, keptback, errors = parse_apt_install(txt)

    type = kwargs.get('type', 'install');
    pkgs = kwargs.get('packages', []);

    if format == 'html':
        return render_to_response('profile/install.html',
                                  {'packages': pkgs,
                                   'extra': extra,
                                   'suggested': suggested,
                                   'recommended': recommended,
                                   'install': install,
                                   'urls': packages,
                                   'newest': newest,
                                   'upgrade': upgrade,
                                   'keptback': keptback,
                                   'errors': errors})
    elif format == 'json':
        data = {'stat': 'ok',
                'type': type,
                'data': {'packages': pkgs,
                         'extra': extra,
                         'suggested': suggested,
                         'recommended': recommended,
                         'install': install,
                         'urls': packages,
                         'newest': newest,
                         'upgrade': upgrade,
                         'keptback': keptback,
                         'errors': errors}}
        jdata = json.dumps(data)
        return render_to_response('profile/json', {'json': jdata},
                                  mimetype='text/plain')

@login_required
@_post
@_profile
@_updated
def install(request, profile):
    format = request.GET.get('format', 'html')
    if not format in ['html', 'json']:
        format = 'html'

    form = InstallForm(request.POST)
    if form.is_valid():
        packages = form.cleaned_data['packages']
        task = tasks.install.delay(profile.id, packages)

        data = {'stat': 'ok',
                'task_id': task.task_id}
        return render_to_response('profile/json', {'json': json.dumps(data)},
                                  mimetype='text/plain')
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('install pid=%d' % profile.pid)

@login_required
@_profile
@_updated
def install_result(request, profile, task_id):
    task = AsyncResult(task_id)
    if task.status == 'SUCCESS':
        pkgs, ret, out, err = task.result
        return _show_install(ret, out, err, 'json', packages=pkgs)
    elif task.status == 'PENDING':
        data = {'stat': 'pending'}
    else:
        data = {'stat': 'fail'}
    return render_to_response('profile/json', {'json': json.dumps(data)},
                              mimetype='text/plain')

@login_required
@_profile
@_updated
def info(request, profile, pkg):
    format = request.GET.get('format', 'html')
    if not format in ['html', 'json']:
        format = 'html'

    path = utils.get_path(profile.pid)
    pkg, code, out, err = apt.show(path, pkg)

    if code == 100: # Not found
        raise Http404()
        
    info, keys = parse_apt_show(out)

    if info is None:
        pkg = None
        sdesc = ''
        desc = ''
        data = []
    else:
        sdesc = info['Description'].split("\n")[0]
        desc = "\n".join(info['Description'].split("\n")[1:])

        data = []
        for key in keys:
            data.append((key, info[key]))

    if format == 'html':
        return render_to_response('profile/info.html',
                                  {'pkg': pkg,
                                   'desc': desc,
                                   'sdesc': sdesc,
                                   'data': data})

    elif format == 'json':
        data = {'stat': 'ok',
                'type': 'pkgshow',
                'data': {'package': pkg,
                         'desc': desc,
                         'sdesc': sdesc,
                         'data': data}}
        jdata = json.dumps(data)
        return render_to_response('profile/json', {'json': jdata},
                                  mimetype='application/json')

@login_required
@_profile
@_updated
def search(request, profile):
    format = request.GET.get('format', 'html')
    if not format in ['html', 'json']:
        format = 'html'

    form = SearchForm(request.POST)
    if form.is_valid():
        packages = form.cleaned_data['packages']
        task = tasks.search.delay(profile.id, packages)

        data = {'stat': 'ok',
                'task_id': task.task_id}
        return render_to_response('profile/json', {'json': json.dumps(data)},
                                  mimetype='text/plain')
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('search pid=%d' % profile.pid)

@login_required
@_profile
@_updated
def search_result(request, profile, task_id):
    task = AsyncResult(task_id)
    if task.status == 'SUCCESS':
        pkgs, ret, out, err = task.result
        pkgs = ' '.join(pkgs)

        return render_to_response('profile/search.json',
                                  {'pkgs': pkgs,
                                   'ret': ret,
                                   'items': parse_apt_search(out)})
    elif task.status == 'PENDING':
        data = {'stat': 'pending'}
    else:
        data = {'stat': 'fail'}
    return render_to_response('profile/json', {'json': json.dumps(data)},
                              mimetype='text/plain')

@login_required
@_post
@_profile
@_pre_updated
def update(request, profile):
    profile.repo_updated = None
    profile.save()

    task = tasks.update.delay(profile.id)
    print 'update:', task.task_id
    profile.tid_update = task.task_id
    profile.save()

    data = {'stat': 'ok',
            'task_id': task.task_id}
    return render_to_response('profile/json', {'json': json.dumps(data)},
                              mimetype='text/plain')

@login_required
@_post
@_profile
def sources(request, profile):
    form = SourcesForm(request.POST)
    if form.is_valid():
        sources = form.cleaned_data['sources']
        path = utils.get_path(profile.pid)
        utils.update_sources(path, sources)
        profile.sources_updated = datetime.now()
        profile.repo_updated = None
        profile.save()
        return redirect(show, profile.pid)
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('sources pid=%d' % profile.pid)

@login_required
@_post
@_profile
def status(request, profile):
    form = UploadStatusForm(request.POST, request.FILES)
    print request.FILES.keys()
    if form.is_valid():
        path = handle_uploaded_status(profile, request.FILES['file'])
        profile.repo_updated = None
        profile.status_updated = datetime.now()

        size, hash = utils.get_status_info(path)
        profile.status_size = size
        profile.status_hash = hash

        profile.save()
        return redirect(show, profile.pid)
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('status pid=%d' % profile.pid)

@login_required
@_profile
def show(request, profile):
    upload_form = UploadStatusForm()

    path = utils.get_path(profile.pid)
    sources = utils.get_repo(path)
    sources_form = SourcesForm({'sources': sources})

    install_form = InstallForm()
    search_form = SearchForm()

    return render_to_response('profile/show.html',
                              {'profile': profile,
                               'upload': upload_form,
                               'sources': sources_form,
                               'install': install_form,
                               'search': search_form},
                              context_instance=RequestContext(request))

@login_required
def index(request):
    form = AddProfileForm()
    if request.method == 'POST':
        form = AddProfileForm(request.POST)
        if form.is_valid():
            profile = Profile()
            profile.user = request.user
            profile.name = form.cleaned_data['name']
            profile.desc = form.cleaned_data['desc']
            profile.arch = form.cleaned_data['arch']

            while True:
                pid = profile.generate_pid()
                if not utils.check_pid(pid):
                    profile.pid = pid
                    break

            profile.save()

            path = utils.get_path(profile.pid)
            utils.prepare_profile_dir(path)
            utils.configure_profile(path, arch=profile.arch)

            return redirect(show, pid)
        
    profiles = Profile.objects.filter(user=request.user)
    return render_to_response('profile/index.html',
                              {'form': form,
                               'profiles': profiles},
                              context_instance=RequestContext(request))
    
