from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .forms import FormRegistro, FormLogin, TransferenciaSaldoForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Transferencia, Transaccion
from django.contrib.auth.models import User
from django.urls import reverse
import random
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction, IntegrationApiKeys, IntegrationCommerceCodes

@login_required(login_url='/login/')
def recarga_saldo(request):
    perfil_usuario_actual = PerfilUsuario.objects.get(usuario=request.user)
    buy_order = str(random.randrange(10000000, 99999999))
    session_id = str(random.randrange(10000000, 99999999))
    amount = int(request.POST.get('amount'))
    return_url = request.build_absolute_uri(reverse('return'))
    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))

    if amount >= 1000 and amount <= 9999999999:
        create_request = {
            "buy_order": buy_order,
            "session_id": session_id,
            "amount": amount,
            "return_url": return_url,
        }
        response = tx.create(buy_order, session_id, amount, return_url)

        transaccion = Transaccion(
            perfil_usuario=perfil_usuario_actual,
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=return_url
        )

        request.session['create_request'] = create_request
        request.session['response'] = response
        request.session['amount'] = amount

        if tx.status:
            messages.success(request, 'La transacción se ha completado correctamente.')
            transaccion.save()          
            return redirect('create')
        else:
            messages.error(request, 'La transacción no se ha podido completar.')
            return render(request, 'transaccion.html')
        
    else:
        messages.error(request, 'El monto no está dentro del rango permitido.')
        return render(request, 'transaccion.html')

def confirma_recarga(request):
    amount = request.session.get('amount')
    create_request = request.session.get('create_request')
    response = request.session.get('response')
    perfil_usuario_actual = PerfilUsuario.objects.get(usuario=request.user)

    perfil_usuario_actual.saldo += amount  
    perfil_usuario_actual.save()
 
    return render(request, 'create.html', {'request': create_request, 'response': response})

# Create your views here.
@login_required(login_url='/login/')
def transaccion(request):
    return render(request, "transaccion.html")

def returnn(request):
    return render(request, "return.html")

def final(request):
    return render(request, "final.html")

def home(request):
    return render(request, "home.html")

def nosotros(request):
    return render(request, "nosotros.html")

def login(request):
    return render(request, "login.html")

def forgot(request):
    return render(request, "forgot.html")

def logout(request):
    return render(request, "logout.html")

def nosotros(request):
    return render(request, "nosotros.html")

def contacto(request):
    return render(request, "contacto.html")

def cuenta(request):
    return render(request, "cuenta.html")

def transferencia(request):
    return render(request, 'transferencia.html')

class VistaRegistro(View):
    form_class = FormRegistro
    initial = {'key': 'value'}
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()

            # Crear un perfil de usuario para el usuario registrado
            perfil_usuario = PerfilUsuario(usuario=user, saldo=10000)
            perfil_usuario.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada exitosamente. Ya puedes ingresar a tu cuenta, {username}.')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')
        
        return super(VistaRegistro, self).dispatch(request, *args, **kwargs)
    
class CustomVistaLogin(LoginView):
    form_class = FormLogin

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomVistaLogin, self).form_valid(form)

@login_required(login_url='/login/')
def transferencia_saldo(request):
    form = TransferenciaSaldoForm()
    error = None

    if request.method == 'POST':
        form = TransferenciaSaldoForm(request.POST)
        if form.is_valid():
            username_destino = form.cleaned_data['username_destino']
            monto_transferencia = form.cleaned_data['monto_transferencia']
            usuario_actual = request.user

            if monto_transferencia > 0:  # Verificar que el monto sea mayor que cero
                try:
                    perfil_usuario_actual = PerfilUsuario.objects.get(usuario=usuario_actual)
                    perfil_usuario_destino = PerfilUsuario.objects.get(usuario__username=username_destino)

                    if usuario_actual != perfil_usuario_destino.usuario:
                        if perfil_usuario_actual.saldo >= monto_transferencia:
                            perfil_usuario_actual.saldo -= monto_transferencia
                            perfil_usuario_destino.saldo += monto_transferencia
                            perfil_usuario_actual.save()
                            perfil_usuario_destino.save()

                            # Registrar la transferencia enviada
                            transferencia = Transferencia.objects.create(
                                destinatario=perfil_usuario_destino,
                                remitente=perfil_usuario_actual,
                                monto=monto_transferencia
                            )

                            messages.success(request, f'Saldo transferido exitosamente a {username_destino}.')
                            return redirect('/')
                        else:
                            messages.error(request, 'Saldo insuficiente para realizar la transferencia.')
                    else:
                        messages.error(request, 'No puedes transferir saldo a ti mismo.')
                except PerfilUsuario.DoesNotExist:
                    messages.error(request, 'El perfil de usuario no existe.')
            else:
                messages.error(request, 'El monto de transferencia debe ser mayor que cero.')
        else:
            messages.error(request, 'Datos inválidos. Verifica los datos ingresados.')

    usuario_actual = request.user
    try:
        perfil_usuario_actual = PerfilUsuario.objects.get(usuario=usuario_actual)
        saldo_actual = perfil_usuario_actual.saldo
    except PerfilUsuario.DoesNotExist:
        saldo_actual = 0
        error = "No existe un perfil de usuario asociado a este usuario. Por favor, inicia sesión."

    return render(request, 'transferencia.html', {'form': form, 'saldo_actual': saldo_actual, 'error': error})

@login_required(login_url='/login/')
def cuenta(request):
    usuario_actual = request.user

    try:
        perfil_usuario_actual = PerfilUsuario.objects.get(usuario=usuario_actual)
        saldo_actual = perfil_usuario_actual.saldo
        transferencias_enviadas = Transferencia.objects.filter(remitente=perfil_usuario_actual).order_by('-fecha')[:5]
        transferencias_recibidas = Transferencia.objects.filter(destinatario=perfil_usuario_actual).order_by('-fecha')[:5]
    except PerfilUsuario.DoesNotExist:
        saldo_actual = 0
        transferencias_enviadas = []
        transferencias_recibidas = []

    return render(request, 'cuenta.html', {'saldo_actual': saldo_actual, 'transferencias_enviadas': transferencias_enviadas, 'transferencias_recibidas': transferencias_recibidas})
