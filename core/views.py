from django.shortcuts import render, redirect
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.views import View
from .forms import FormRegistro, FormLogin
from django.contrib.auth.views import LoginView
from transbank.transaccion_completa.transaction import Transaction


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
            form.save()

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
    