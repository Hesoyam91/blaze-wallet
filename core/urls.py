from django.contrib import admin
from django.urls import path
from core import views
from core.views import VistaRegistro, CustomVistaLogin
from core.forms import FormLogin
from django.contrib.auth import views as authViews
from .views import transferencia_saldo



urlpatterns = [
    path('', views.home, name="home"),
    path('nosotros/', views.nosotros, name="nosotros"),
    path('login/', CustomVistaLogin.as_view(redirect_authenticated_user=True, template_name='login.html',
                                           authentication_form=FormLogin), name='login'),
    path('logout/', authViews.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', VistaRegistro.as_view(), name='register'),
    path('forgot/', views.forgot, name="forgot"),
    path('contacto/', views.contacto, name="contacto"),
    path('cuenta/', views.cuenta, name="cuenta"),
    path('transferencia/', transferencia_saldo, name='transferencia_saldo'),
    path('beatpay/', views.beatpay, name="beatpay"),
    path('return/', views.returnn, name="return")
    ]

handler404 = views.handler404