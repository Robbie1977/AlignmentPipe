from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect

def home(request):
  return HttpResponseRedirect('/admin')
  # if not request.user == '':
  #   try:
  #     fn = User.objects.filter(username=request.user).values('first_name', 'last_name')[0]
  #   except:
  #     fn = {'first_name':'Unknown','last_name':'User'}
  #   context = RequestContext(request,
  #                          {'request': request,
  #                           'user': request.user}.update(fn))
  # else:
  #   context = RequestContext(request,
  #                          {'request': request,
  #                           'user': request.user})
  # return render_to_response('home.html',
  #                            context_instance=context)
