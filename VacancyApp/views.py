from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
import requests

def home(request):
    context={'ip':request.META.get('REMOTE_ADDR')}
    return render(request,'base.html',context)