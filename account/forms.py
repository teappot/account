import random
import string
import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _

from django.conf import settings
    
CLASS_FORM_CONTROL = "form-control"
CLASS_TEXT_LOWERCASE = "text-lowercase"
LABEL_USERNAME = "Correo electrónico" if settings.AUTH_EMAIL_AS_USERNAME else "Nombre de usuario"

class LoginForm(forms.Form):

    username = forms.CharField(
        label = _(f"{LABEL_USERNAME}"),
        widget = forms.TextInput(attrs={ 'placeholder': _(f"{LABEL_USERNAME}"), 'required': True, 'max_length': 96, 'class': f"{CLASS_FORM_CONTROL} {CLASS_TEXT_LOWERCASE}" }) 
    )

    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(attrs={ 'placeholder': _("Password"), 'required': True, 'max_length': 48, 'class': f"{CLASS_FORM_CONTROL}" }) 
    )

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(_("El usuario o password no corresponde")) 
            if not user.is_active:
                raise forms.ValidationError(_("Esta cuenta no está activa"))
            
        return cleaned_data
    
class CreateForm(forms.Form):
    
    username = forms.CharField(
        label = _(f"{LABEL_USERNAME}"),
        widget = forms.TextInput(
            attrs={ 'placeholder': _(f"{LABEL_USERNAME}"), 'required': True, 'max_length': 96, 'class': f"{CLASS_FORM_CONTROL} {CLASS_TEXT_LOWERCASE}" })
    )
    
    if not settings.AUTH_EMAIL_AS_USERNAME:
        email = forms.EmailField(
            label = _("Correo"),
            widget = forms.TextInput(attrs={ 'placeholder': _("Correo"), 'required': True, 'max_length': 96, 'class': f"{CLASS_FORM_CONTROL} {CLASS_TEXT_LOWERCASE}" }) 
        )

    if settings.AUTH_AUTO_ACTIVATE:
        password = forms.CharField(
            label = _("Password"),
            widget = forms.PasswordInput(attrs={ 'placeholder': _("Password"), 'required': True, 'max_length': 48, 'class': f"{CLASS_FORM_CONTROL}" }) 
        )

        password_confirm = forms.CharField(
            label = "Confirme su password", 
            widget = forms.PasswordInput(attrs={ 'placeholder': _("Confirme su password"), 'required':True, 'max_length': 48, 'class': f"{CLASS_FORM_CONTROL}" })
        )

    field_order = ['email', 'username', 'password', 'password_confirm']

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_("Este nombre de usuario ya está utilizado. Intente iniciar sesión o recuperar su acceso."))

        if not re.match(r'^[a-zA-Z0-9._]+$', username):
            raise forms.ValidationError(_("El nombre de usuario solo puede contener letras, números, puntos y guiones bajos."))

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if settings.AUTH_EMAIL_AS_USERNAME and User.objects.filter(username=email).count() > 0:
            raise forms.ValidationError(_("Este email ya está utilizado. Intente iniciar sesión o recuperar su acceso."))
        
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)
        
        return password

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_confirm')
        if password_repeat != password:
            raise forms.ValidationError(_("El password no coincide"))
        
        return password_repeat

    def clean(self):
        if settings.AUTH_EMAIL_AS_USERNAME:
            self.cleaned_data['username'] = self.cleaned_data.get('email')
        if not settings.AUTH_AUTO_ACTIVATE:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            self.cleaned_data['password'] = password
            self.cleaned_data['password_confirm'] = password

        return super().clean()

class UserTaskRequestForm(forms.Form):
    
    username = forms.CharField(
        label = _(f"{LABEL_USERNAME}"),
        widget=forms.TextInput(attrs={ 'placeholder': _(f"{LABEL_USERNAME}"), 'required':True, 'max_length':96, 'class': f"{CLASS_FORM_CONTROL} {CLASS_TEXT_LOWERCASE}" } ) 
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if User.objects.filter(username=username).count() == 0 and User.objects.filter(email=username).count() == 0:
            raise forms.ValidationError(_("El nombre de usuario o correo no existe"))

        return cleaned_data
    
class RecoveryForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.user_task_token = kwargs.pop('user_task_token', None)
        super().__init__(*args, **kwargs)
    
    password_new = forms.CharField(
        label = _("Nuevo Password"),
        widget = forms.PasswordInput(attrs={ 'placeholder': _("Nuevo Password"), 'required': True, 'max_length': 48, 'class': f"{CLASS_FORM_CONTROL}" }) 
    )

    password_repeat = forms.CharField(
        label = _("Confirma tu nuevo Password"),
        widget = forms.PasswordInput(attrs={ 'placeholder': _("Confirma tu nuevo Password"), 'required': True, 'max_length': 48, 'class': f"{CLASS_FORM_CONTROL}" }) 
    )

    def clean_password_new(self):
        password_new = self.cleaned_data.get('password_new')
        try:
            validate_password(password_new)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)
        
        return password_new

    def clean_password_repeat(self):
        password_new = self.cleaned_data.get('password_new')
        password_repeat = self.cleaned_data.get('password_repeat')
        if password_repeat != password_new:
            raise forms.ValidationError(_("El password no coincide"))
        
        return password_repeat
     
    def clean(self):
        cleaned_data = super().clean()
        
        if self.user_task_token is None:
            raise forms.ValidationError(_("El token no es válido "))
        
        if self.user_task_token.state != "ACTIVE":
            raise forms.ValidationError(_("El token está expirado "))

        return cleaned_data