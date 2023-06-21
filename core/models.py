from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.IntegerField(default=10000)

    def __str__(self):
        return self.usuario.username

class Transferencia(models.Model):
    destinatario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='transferencias_recibidas')
    remitente = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='transferencias_enviadas')
    monto = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transferencia de {self.remitente.usuario.username} a {self.destinatario.usuario.username}"
    
class Transaccion(models.Model):
    perfil_usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    buy_order = models.CharField(max_length=50)
    session_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    return_url = models.URLField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaccion de {self.perfil_usuario.usuario.username} - ID: {self.id}"
