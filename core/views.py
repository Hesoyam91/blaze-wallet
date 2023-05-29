from django.shortcuts import render
from django.shortcuts import render, HttpResponse


# Create your views here.
def home(request):
    return render(request, "home.html")

def nosotros(request):
    return render(request, "nosotros.html")

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def forgot(request):
    return render(request, "forgot.html")