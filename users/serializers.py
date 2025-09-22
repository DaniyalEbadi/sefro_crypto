from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=150, help_text="Username or email address")
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class ProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class PremiumGrantSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    days = serializers.IntegerField(default=365, min_value=1)


class TestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, help_text="Email address to send test email to. Defaults to user's email.")


# Response serializers
class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ProfileResponseSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    is_premium = serializers.BooleanField()
    premium_expires_at = serializers.DateTimeField(allow_null=True)


class PremiumStatusResponseSerializer(serializers.Serializer):
    is_premium = serializers.BooleanField()
    premium_expires_at = serializers.DateTimeField(allow_null=True)


class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class TestEmailResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()