from itertools import chain
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
import requests
from .forms import FormRegistro, FormLogin, TransferenciaSaldoForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Transferencia, Transaccion, TransferenciaBeatpay
from django.conf import settings
from django.template import RequestContext
import stripe
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
stripe.api_key = settings.STRIPE_SECRET_KEY

@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'banco_origen': openapi.Schema(type=openapi.TYPE_STRING),
            'tarjeta_origen': openapi.Schema(type=openapi.TYPE_STRING),
            'tarjeta_destino': openapi.Schema(type=openapi.TYPE_STRING),
            'monto': openapi.Schema(type=openapi.TYPE_INTEGER),
            'comentario': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['banco_origen', 'tarjeta_origen', 'tarjeta_destino', 'monto'],
    ),
    responses={
        200: openapi.Response(description='Transferencia exitosa.'),
        405: openapi.Response(description='Método no permitido.'),
    }
)
@api_view(['POST'])
def vista_api(request):
    if request.method == 'POST':
        datos = request.data
        # Procesa los datos según tus necesidades
        banco_origen = datos.get('banco_origen')
        tarjeta_origen = datos.get('tarjeta_origen')
        tarjeta_destino = datos.get('tarjeta_destino')
        monto = datos.get('monto')
        comentario = datos.get('comentario', '')

        try:
            perfil_destino = PerfilUsuario.objects.get(usuario__username=tarjeta_destino)
            perfil_destino.saldo += monto
            perfil_destino.save()

            transferencia_beatpay = TransferenciaBeatpay.objects.create(
                destinatario=tarjeta_destino,
                remitente_str=tarjeta_origen,
                monto=monto,
                comentario=comentario
                )
            
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'La tarjeta de destino no existe'}, status=400)


        response_data = {
            "status": "success",
            "code": "201"
        }

        return Response(response_data, status=200)

    return Response({'error': 'Método no permitido'}, status=405)






@login_required(login_url='/login/')
def recharge(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        amount_clp = request.POST.get('amount')
        usuario = request.user
        actual_user = PerfilUsuario.objects.get(usuario=usuario)

        if token and int(amount_clp) >= 1000:
            # Convertir el monto de CLP a USD
            amount_usd = int(amount_clp) / 800

            try:
                # Crear la transferencia en Stripe utilizando el monto en USD
                transfer = stripe.Charge.create(
                    amount=int(amount_usd * 100),  # Convertir el monto a centavos
                    currency='usd',  # Utilizar la moneda deseada (USD)
                    source=token
                )

                actual_user.saldo += int(amount_clp)
                actual_user.save()
                # Proceso exitoso de transferencia
                return render(request, 'success.html')
                
            
            except stripe.error.CardError as e:
                error_message = e.error.message
                return render(request, 'error.html', {'error_message': error_message})
            
            except Exception as e:
                # Otro tipo de error
                error_message = str(e)
                return redirect('recharge')

        else:
            messages.error(request, 'Monto es menor a $1000.')
            return redirect('recharge')
    
    else:
        return render(request, 'recharge.html')



def success(request):
    return render(request, 'success.html')

@login_required(login_url='/login/')
def beatpay(request):
    response_data = None  # Valor predeterminado para response_data

    usuario = request.user
    tarjeta_origen = PerfilUsuario.objects.get(usuario=usuario)
    saldo = tarjeta_origen.saldo

    if request.method == 'POST':
        # Obtener los datos del formulario
        tarjeta_destino = request.POST.get('tarjeta_destino')
        comentario = request.POST.get('comentario')
        monto = request.POST.get('monto')

        saldo = int(saldo)
        monto = int(monto)

 
        if saldo >= monto:
            codigo = 'DEMOTESTCORRECTO'
            token = 'DEMOTESTCORRECTO'
            if codigo == 'DEMOTESTCORRECTO' and token == 'DEMOTESTCORRECTO':
                url = 'https://musicpro.bemtorres.win/api/v1/tarjeta/transferir'
                data = {
                    'tarjeta_origen': tarjeta_origen,
                    'tarjeta_destino': tarjeta_destino,
                    'comentario': comentario,
                    'monto': monto,
                    'codigo': codigo,
                    'token': token
                }
                response = requests.post(url, data=data)
                response_data = response.json()
                print(response_data)  # Imprimir la respuesta en la consola del servidor
                if 'status' in response_data['response'] and response_data['response']['status'] == 200:
                    tarjeta_origen.saldo -= monto
                    tarjeta_origen.save()
                    # Registrar la transferencia enviada
                    transferencia_beatpay = TransferenciaBeatpay.objects.create(
                        destinatario=tarjeta_destino,
                        remitente=tarjeta_origen,
                        monto=monto,
                        comentario=comentario
                    )

                    messages.success(request, f'Saldo transferido exitosamente a {tarjeta_destino}.')
                    return redirect('/')
                else:
                    if 'message' in response_data['response']:
                        messages.error(request, response_data['response']['message'])
                    else:
                        messages.error(request, 'Ocurrió un error en la transferencia.')
                return render(request, 'beatpay.html', {'response_data': response_data})
            else:
                messages.error(request, 'Código o Token incorrecto.')
        else:
            messages.error(request, 'Saldo insuficiente para realizar la transferencia.')

    return render(request, 'beatpay.html', {'response_data': response_data, 'tarjeta_origen': tarjeta_origen})


def handler404(request, *args, **argv):
    response = render('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
    
def returnn(request):
    return render(request, "return.html")

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
        transferencias_enviadas_beatpay = TransferenciaBeatpay.objects.filter(remitente=perfil_usuario_actual).order_by('-fecha')[:5]
        all_transferencias_enviadas = sorted(
            chain(transferencias_enviadas, transferencias_enviadas_beatpay),
            key=lambda transferencia: transferencia.fecha,
            reverse=True
        )[:5]
        transferencias_recibidas = Transferencia.objects.filter(destinatario=perfil_usuario_actual).order_by('-fecha')[:5]
        transferencias_recibidas_beatpay = TransferenciaBeatpay.objects.filter(destinatario=perfil_usuario_actual).order_by('-fecha')[:5]
        all_transferencias_recibidas = sorted(
            chain(transferencias_recibidas, transferencias_recibidas_beatpay),
            key=lambda transferencia: transferencia.fecha,
            reverse=True
        )[:5]
    except PerfilUsuario.DoesNotExist:
        saldo_actual = 0
        transferencias_enviadas = []
        transferencias_recibidas = []

    return render(request, 'cuenta.html', {'saldo_actual': saldo_actual, 'transferencias_enviadas': all_transferencias_enviadas, 'transferencias_recibidas': all_transferencias_recibidas})
