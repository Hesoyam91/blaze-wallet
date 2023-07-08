from django.contrib import admin
from django.urls import path
from core import views
from core.views import VistaRegistro, CustomVistaLogin
from core.forms import FormLogin
from django.contrib.auth import views as authViews
from .views import transferencia_saldo
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path, include


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API Documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="uwu@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

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
    path('return/', views.returnn, name="return"),
    path('recharge/', views.recharge, name="recharge"),
    path('success/', views.success, name="success"),
    path('api/v1/transferencia', views.vista_api, name='transferencia-api'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

handler404 = views.handler404

