from django.contrib import admin
from .models import PerfilUsuario, Transferencia, Transaccion

admin.site.register(PerfilUsuario)
admin.site.register(Transferencia)
admin.site.register(Transaccion)
