import secrets
import string

from django.http import HttpRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.urls import reverse
from django.template.loader import render_to_string
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User

from django.conf import settings
from teacore.extras import async_send_mail, hx_redirect
from .forms import CreateForm, LoginForm, RecoveryForm, UserTaskRequestForm
from .models import UserTaskToken

@login_required(login_url='account:login')
def index(request):
    if settings.USER_DEFAULT_HOME is not None:
        return hx_redirect(settings.USER_DEFAULT_HOME)
        
    return render(request, "account/index.html")

def login(request):
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username=form.cleaned_data['username'].lower()
            password=form.cleaned_data['password']
            
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            
            redirect = request.POST.get("next", None)
            try:
                if redirect is not None:
                    return hx_redirect(redirect)
            except Exception:
                pass
            
            return hx_redirect(settings.AUTH_DEFAULT_REDIRECT)
    else:   
        username = request.GET.get("username", None)
        if username is not None:
            form = LoginForm({ 'username': username })
        else:
            form = LoginForm()

    return render(request, "account/forms/login.html", { 'form': form })

@csrf_exempt
def auth_google(request):

    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']
 
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError:
        return HttpResponse(status=403)
 
    email = user_data['email']
    given_name = user_data.get('given_name', '')
    family_name = user_data.get('family_name', '')
    
    user = User.objects.filter(username=email).first()

    if not user:
        allowed_chars = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(allowed_chars) for _ in range(16))
        user = User.objects.create_user(username=email, email=email, password=password, first_name=given_name, last_name=family_name)
        user.save()

    if user.first_name == "": user.first_name = given_name
    if user.last_name == "": user.last_name = family_name
    user.save()

    auth.login(request, user)
    
    return hx_redirect(settings.AUTH_DEFAULT_REDIRECT)

"""
Register
"""
def register(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if settings.AUTH_AUTO_ACTIVATE:
                
                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)

                return hx_redirect(settings.AUTH_DEFAULT_REDIRECT)
            
            recovery_task_token = UserTaskToken.new_recovery_token(username=username)
            recovery_send_mail(recovery_task_token)

            return render(request, "account/pages/recovery.html")
        
    else:
        form = CreateForm(request.GET) if request.GET else CreateForm()

    return render(request, "account/forms/register.html", { 'form': form })


"""
Recovery 
"""
def recovery(request, username=None, token=None):
    if username and token:
        return recovery_validate(request, username, token)
    
    if request.method == 'POST':
        form = UserTaskRequestForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            recovery_task_token = UserTaskToken.new_recovery_token(username=username)
            recovery_send_mail(recovery_task_token)
            
            return render(request, "account/pages/recovery.html")

    else:   
        form = UserTaskRequestForm(request.GET) if request.GET else UserTaskRequestForm()

    return render(request, "account/forms/recovery.html", { 'form': form })


def recovery_validate(request, username, token):
    
    user_task_token = UserTaskToken.get_recovery_token(username=username, token=token)

    if user_task_token is None or user_task_token.state != "ACTIVE":
        messages.error(request, _("Token de recuperación inválido, solicite uno nuevamente"))
        return hx_redirect(reverse("account:recovery"))

    if request.method == 'POST':
        form = RecoveryForm(request.POST, user_task_token=user_task_token)

        if form.is_valid():
            password_new = form.cleaned_data['password_new']
            user_task_token.use_recovery_token(password_new)

            messages.info(request, _("Password cambiado correctamente. Inicie sesión en la aplicación con su nuevo password."))
            
            return hx_redirect("account:login")
    else:   
        form = RecoveryForm()

    return render(request, "account/forms/recovery.html", { 'form': form })

"""
logout
"""
def logout(request):
    auth.logout(request)
    messages.info(request, _("Sesión cerrada"))

    return hx_redirect("/")

"""
Apoyo
"""
def recovery_send_mail(task_token:UserTaskToken):
    message = render_to_string("account/mails/recovery.html", {
        'username': task_token.user.email,
        'url': settings.APP_HOST + reverse("account:recovery", args=[
            task_token.user.username, task_token.token])
    }, request=HttpRequest())

    async_send_mail(
        subject = f"{_('Solicitud de Acceso')} | {settings.APP_TITLE}", 
        message = message, 
        recipient_list = [task_token.user.email]
    )