from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def say_hello(request):
    return HttpResponse("Hello world")


def welcome(request, name):
    return render(request, 'index.html', {"name": name})
