from django.contrib import admin
from .models import PerfilUsuario, Transferencia, Transaccion, TransferenciaBeatpay

admin.site.register(PerfilUsuario)
admin.site.register(Transferencia)
admin.site.register(Transaccion)
admin.site.register(TransferenciaBeatpay)
