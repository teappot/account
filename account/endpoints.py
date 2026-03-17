from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import api

app_name = "auth-api"
urlpatterns = [
    
    path("register/", api.UserRegistrationAPIView.as_view(), name="register"),
    path("recovery/", api.UserRecoveryAPIView.as_view(), name="recovery"),
    path("login/", api.UserLoginAPIView.as_view(), name="login"),
    path("login-google/", api.UserLoginGoogleAPIView.as_view(), name="login-google"),

    path("logout/", api.UserLogoutAPIView.as_view(), name="logout"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token-refresh"),
       
]