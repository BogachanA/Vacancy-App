from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import logout


def home(request):
    context={'ip':request.META.get('REMOTE_ADDR')}
    return render(request,'base.html',context)

def log_out(request):
    logout(request)
    print("logging out")
    return HttpResponseRedirect('/')


def login_error(request):
        return HttpResponse("Login error. You are not allowed.")


