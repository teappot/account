from django.contrib.auth.models import User
from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from .views import recovery_send_mail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        password = attrs.get("password1", "")
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise serializers.ValidationError(
                _(f"Passwords must be at least {settings.PASSWORD_MIN_LENGTH} characters."))

        return attrs

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        user = User.objects.create_user(password=password, email=username, =False, **validated_data)
        recovery_send_mail(user)
        
        return user

class UserRecoverySerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    
    class Meta:
        model = User
        fields = ["username"]

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        
        if user is None:
            raise exceptions.AuthenticationFailed(detail=_('User does not exist.'))

        recovery_send_mail(user)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        
        raise exceptions.AuthenticationFailed()
    
class UserLoginGoogleSerializer(serializers.Serializer):
    id_token = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            response = id_token.verify_oauth2_token(data['id_token'], requests.Request(), audience=None)
            return User.objects.get(username=response['email'])
        except Exception as e:
            raise exceptions.AuthenticationFailed(detail=e) 