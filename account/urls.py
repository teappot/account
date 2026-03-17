from django.urls import path
from django.conf import settings
from . import views

app_name = "account"
urlpatterns = [
    path('', views.index, name='index'),
]

if settings.AUTH_BACKOFFICE:
    urlpatterns+= path('login/', views.login, name='login'),
    urlpatterns+= path('logout/', views.logout, name='logout'),
    urlpatterns+= path('auth/google', views.auth_google, name='auth-google'),
if settings.AUTH_SELF_CREATE:
    urlpatterns+= path('register/', views.register, name='register'),
if settings.AUTH_SELF_RECOVERY:
    urlpatterns+= path('recovery/', views.recovery, name='recovery'),
    urlpatterns+= path('recovery/username:<str:username>/token:<str:token>/', views.recovery, name='recovery'),