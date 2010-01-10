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

from gerobak import utils, apt
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
        profile = get_object_or_404(Profile, pk=pid)
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
            return redirect(show, profile.id)

        return func(request, profile, *args, **kwargs)
    return _func

def _pre_updated(func):
    def _func(request, profile, *args, **kwargs):
        if profile.status_updated is None or \
           profile.sources_updated is None:
            
            request.user.message_set.create(message="status or sources is missing")
            return redirect(show, profile.id)

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

    path = utils.get_path(profile.id)
    status = file.temporary_file_path()

    tmp = None
    if file.name.endswith('.gz') or file.name.endswith('.bz2'):
        tmp = _decompress(file.name, file.temporary_file_path())
        utils.update_status(path, tmp)
        os.unlink(tmp)

    else:
        utils.update_status(path, status)

    return path

@login_required
@_post
@_profile
@_updated
def install(request, profile):
    form = InstallForm(request.POST)
    if form.is_valid():
        packages = form.cleaned_data['packages']
        path = utils.get_path(profile.id)
        pkgs, ret, out, err = apt.install(path, packages)

        pkgs = ' '.join(pkgs)

        return render_to_response('profile/install.html', 
                                  {'pkgs': pkgs,
                                   'ret': ret,
                                   'out': out,
                                   'err': err})
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('install pid=%d' % profile.id)

@login_required
@_profile
@_updated
def info(request, profile, pkg):
    format = request.GET.get('format', 'html')
    if not format in ['html', 'json']:
        format = 'html'

    path = utils.get_path(profile.id)
    pkg, code, out, err = apt.show(path, pkg)

    if code == 100: # Not found
        raise Http404()
        
    info, keys = parse_apt_show(out)

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
        print jdata
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
        path = utils.get_path(profile.id)
        pkgs, ret, out, err = apt.search(path, packages)

        pkgs = ' '.join(pkgs)

        return render_to_response('profile/search.%s' % format, 
                                  {'pkgs': pkgs,
                                   'ret': ret,
                                   'items': parse_apt_search(out)})
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('search pid=%d' % profile.id)

@login_required
@_post
@_profile
@_pre_updated
def update(request, profile):
    path = utils.get_path(profile.id)
    ret, out, err = apt.update(path)

    profile.repo_updated = datetime.now()
    profile.save()

    return render_to_response('profile/update.html', 
                              {'ret': ret,
                               'out': out,
                               'err': err})

@login_required
@_post
@_profile
def sources(request, profile):
    form = SourcesForm(request.POST)
    if form.is_valid():
        sources = form.cleaned_data['sources']
        path = utils.get_path(profile.id)
        utils.update_sources(path, sources)
        profile.sources_updated = datetime.now()
        profile.repo_updated = None
        profile.save()
        return redirect(show, profile.id)
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('sources pid=%d' % profile.id)

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
        return redirect(show, profile.id)
    else:
        print "invalid"
        print form.as_p()
    return HttpResponse('status pid=%d' % profile.id)

@login_required
@_profile
def show(request, profile):
    upload_form = UploadStatusForm()

    path = utils.get_path(profile.id)
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
            profile.save()

            path = utils.get_path(profile.id)
            utils.prepare_profile_dir(path)

            return redirect(index)
        
    profiles = Profile.objects.filter(user=request.user)
    return render_to_response('profile/index.html',
                              {'form': form,
                               'profiles': profiles},
                              context_instance=RequestContext(request))
    
