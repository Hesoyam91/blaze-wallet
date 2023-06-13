from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .forms import FormRegistro, FormLogin, TransferenciaSaldoForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario
from django.contrib.auth.models import User

# Create your views here.
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

def transferencia_exitosa(request):
    return render(request, 'transferencia_exitosa.html')

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
            messages.success(request, f'Cuenta creada exitosamente. Bienvenido/a {username}.')

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


@login_required
def transferencia_saldo(request):
    if request.method == 'POST':
        form = TransferenciaSaldoForm(request.POST)
        if form.is_valid():
            username_destino = form.cleaned_data['username_destino']
            monto_transferencia = form.cleaned_data['monto_transferencia']
            usuario_actual = request.user
            try:
                perfil_usuario_actual = PerfilUsuario.objects.get(usuario=usuario_actual)
                perfil_usuario_destino = PerfilUsuario.objects.get(usuario__username=username_destino)
                
                if usuario_actual != perfil_usuario_destino.usuario:
                    if perfil_usuario_actual.saldo >= monto_transferencia:
                        perfil_usuario_actual.saldo -= monto_transferencia
                        perfil_usuario_destino.saldo += monto_transferencia
                        perfil_usuario_actual.save()
                        perfil_usuario_destino.save()
                        
                        messages.success(request, f'Saldo transferido exitosamente a {username_destino}.')
                        return redirect('transferencia_exitosa')
                    else:
                        messages.error(request, 'Saldo insuficiente para realizar la transferencia.')
                else:
                    messages.error(request, 'No puedes transferir saldo a ti mismo.')
            except PerfilUsuario.DoesNotExist:
                messages.error(request, 'El perfil de usuario no existe.')
        else:
            messages.error(request, 'Formulario inválido. Verifica los datos ingresados.')
    else:
        form = TransferenciaSaldoForm()
    
    return render(request, 'transferencia.html', {'form': form})
