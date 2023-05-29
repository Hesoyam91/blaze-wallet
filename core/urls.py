from django.contrib import admin
from django.urls import path
from core import views


urlpatterns = [
    path('', views.home, name="home"),
    path('nosotros/', views.nosotros, name="nosotros"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('forgot/', views.forgot, name="forgot"),
    ]