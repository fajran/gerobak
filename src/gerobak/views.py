from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

def index(request):
    if request.user.is_authenticated():
        return redirect('gerobak.apps.profile.views.index')
    return redirect('/doc/howto/')
    #return render_to_response('index.html',
    #                          context_instance=RequestContext(request))

