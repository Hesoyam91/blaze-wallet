import random
from django.shortcuts import render, redirect
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.views import View
from .forms import FormRegistro, FormLogin
from django.contrib.auth.views import LoginView



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

def transbank(request):
    return render(request, "transbank.html")

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
    


import requests

def get_ws(data, method, type, endpoint):
    if type == 'live':
        TbkApiKeyId = '597055555532'
        TbkApiKeySecret = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
        url = 'https://webpay3g.transbank.cl' + endpoint  # Live
    else:
        TbkApiKeyId = '597055555532'
        TbkApiKeySecret = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
        url = 'https://webpay3gint.transbank.cl' + endpoint  # Testing

    headers = {
        'Tbk-Api-Key-Id': TbkApiKeyId,
        'Tbk-Api-Key-Secret': TbkApiKeySecret,
        'Content-Type': 'application/json'
    }

    response = requests.request(method, url, headers=headers, data=data)
    return response.json()

def my_account(request):
    baseurl = "https://" + request.get_host() + request.path
    url = "https://webpay3g.transbank.cl/"  # Live
    url = "https://webpay3gint.transbank.cl/"  # Testing

    action = request.GET.get("action", "init")
    message = None
    post_array = False

    if action == "init":
        message += 'init'
        buy_order = random.randint(1, 1000000)
        session_id = random.randint(1, 1000000)
        amount = 15000
        return_url = baseurl + "?action=getResult"
        type = "sandbox"
        data = {
            "buy_order": buy_order,
            "session_id": session_id,
            "amount": amount,
            "return_url": return_url
        }
        method = 'POST'
        endpoint = '/rswebpaytransaction/api/webpay/v1.0/transactions'

        response = get_ws(data, method, type, endpoint)
        message += "<pre>"
        message += str(response)
        message += "</pre>"
        url_tbk = response['url']
        token = response['token']
        submit = 'Continuar!'

    elif action == "getResult":
        message += "<pre>" + str(request.POST) + "</pre>"
        if 'token_ws' not in request.POST:
            return

        token = request.POST.get('token_ws')

        request_data = {
            "token": request.POST.get('token_ws')
        }
        data = ''
        method = 'PUT'
        type = 'sandbox'
        endpoint = '/rswebpaytransaction/api/webpay/v1.0/transactions/' + token

        response = get_ws(data, method, type, endpoint)

        message += "<pre>"
        message += str(response)
        message += "</pre>"

        url_tbk = baseurl + "?action=getStatus"
        submit = 'Ver Status!'

    elif action == "getStatus":
        if 'token_ws' not in request.POST:
            return

        token = request.POST.get('token_ws')

        request_data = {
            "token": request.POST.get('token_ws')
        }
        data = ''
        method = 'GET'
        type = 'sandbox'
        endpoint = '/rswebpaytransaction/api/webpay/v1.0/transactions/' + token

        response = get_ws(data, method, type, endpoint)

        message += "<pre>"
        message += str(response)
        message += "</pre>"

        url_tbk = baseurl + "?action=refund"
        submit = 'Refund!'

    elif action == "refund":
        if 'token_ws' not in request.POST:
            return

        token = request.POST.get('token_ws')

        request_data = {
            "token": request.POST.get('token_ws')
        }
        amount = 15000
        data = {
            "amount": amount
        }
        method = 'POST'
        type = 'sandbox'
        endpoint = '/rswebpaytransaction/api/webpay/v1.0/transactions/' + token + '/refunds'

        response = get_ws(data, method, type, endpoint)

        message += "<pre>"
        message += str(response)
        message += "</pre>"
        submit = 'Crear nueva!'
        url_tbk = baseurl

    return render(request, 'my_account.html', {
        'message': message,
        'url_tbk': url_tbk,
        'token': token,
        'submit': submit
    })
