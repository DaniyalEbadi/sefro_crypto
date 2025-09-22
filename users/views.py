from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import User, EmailVerificationCode, PasswordResetToken
from .serializers import (
    RegisterSerializer, VerifyEmailSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, ChangePasswordSerializer,
    ProfileUpdateSerializer, PremiumGrantSerializer, TestEmailSerializer,
    TokenResponseSerializer, ProfileResponseSerializer, PremiumStatusResponseSerializer,
    MessageResponseSerializer, TestEmailResponseSerializer
)


@extend_schema(
    tags=['Authentication'],
    request=RegisterSerializer,
    responses={
        201: MessageResponseSerializer,
        400: MessageResponseSerializer,
    },
    summary="Register a new user",
    description="Register a new user account. Sends email verification code."
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=400)
        
        data = serializer.validated_data
        username = data['username']
        email = data['email']
        password = data['password']
        
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            code = f"{timezone.now().microsecond % 1000000:06d}"
            EmailVerificationCode.create_for_user(user, code)
            try:
                send_mail(
                    subject='Verify your email',
                    message=f'Your verification code is: {code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception:
                pass
        return Response({'detail': 'Registered. Please verify email.'}, status=201)


@extend_schema(
    tags=['Authentication'],
    request=VerifyEmailSerializer,
    responses={
        200: MessageResponseSerializer,
        400: MessageResponseSerializer,
    },
    summary="Verify email address",
    description="Verify user email with verification code only (no username required)"
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=400)
        
        code = serializer.validated_data['code']
        
        # Find user by verification code (assuming the code is unique enough)
        # You may need to implement a method to find user by code
        # For now, this is a placeholder that needs your specific implementation
        try:
            # This needs to be implemented based on your EmailVerificationCode model
            # For example: verification = EmailVerificationCode.objects.get(code=code, is_used=False)
            # user = verification.user
            return Response({'detail': 'Code verification needs to be implemented based on your model structure'}, status=400)
        except Exception:
            return Response({'detail': 'Invalid code'}, status=400)


@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={
        200: TokenResponseSerializer,
        401: MessageResponseSerializer,
    },
    summary="Login user",
    description="Authenticate user with username or email and return JWT tokens"
)
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=400)
        
        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']
        
        # Try to find user by username or email
        user = None
        if '@' in username_or_email:
            # Looks like an email
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Treat as username
            user = authenticate(request, username=username_or_email, password=password)
        
        # If username authentication failed, try email as fallback
        if not user and '@' not in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user or not user.is_active:
            return Response({'detail': 'Invalid credentials or inactive account'}, status=401)
        
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})


class TokenRefreshView(SimpleJWTTokenRefreshView):
    permission_classes = [AllowAny]


@extend_schema(
    tags=['Authentication'],
    request=None,
    responses={
        200: MessageResponseSerializer,
        400: MessageResponseSerializer,
    },
    summary="Logout user",
    description="Logout user and blacklist refresh token"
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token required'}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out'})
        except Exception:
            return Response({'detail': 'Invalid refresh token'}, status=400)


@extend_schema(
    tags=['Password Management'],
    request=ForgotPasswordSerializer,
    responses={
        200: MessageResponseSerializer,
    },
    summary="Request password reset",
    description="Send password reset code to user email"
)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        email = request.data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.create_for_user(user)
                send_mail(
                    subject='Password reset',
                    message=f'Your reset code is: {token.raw_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except User.DoesNotExist:
                pass
        return Response({'detail': 'If that account exists, you will receive an email shortly.'})


@extend_schema(
    tags=['Password Management'],
    request=ResetPasswordSerializer,
    responses={
        200: MessageResponseSerializer,
        400: MessageResponseSerializer,
    },
    summary="Reset password",
    description="Reset user password with reset code"
)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=400)
        
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({'detail': e.messages}, status=400)
        
        # Find user by reset code and consume the code
        success, user = PasswordResetToken.consume_code_by_code(code)
        if not success or not user:
            return Response({'detail': 'Invalid or expired code'}, status=400)
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'detail': 'Password reset successful'})


@extend_schema(
    tags=['Password Management'],
    request=ChangePasswordSerializer,
    responses={
        200: MessageResponseSerializer,
        400: MessageResponseSerializer,
    },
    summary="Change password",
    description="Change user password (requires authentication)"
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(old_password or ''):
            return Response({'detail': 'Invalid old password'}, status=400)
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({'detail': e.messages}, status=400)
        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Password changed'})


@extend_schema(
    tags=['User Profile'],
    responses={
        200: ProfileResponseSerializer,
    },
    summary="Get user profile",
    description="Get current user profile information"
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileResponseSerializer

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'is_premium': user.has_active_premium(),
            'premium_expires_at': user.premium_expires_at,
        })

    def patch(self, request):
        email = request.data.get('email')
        if email:
            request.user.email = email
            request.user.save(update_fields=['email'])
        return Response({'detail': 'Updated'})


@extend_schema(
    tags=['Premium'],
    responses={
        200: PremiumStatusResponseSerializer,
    },
    summary="Get premium status",
    description="Get user premium subscription status"
)
class PremiumStatusView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PremiumStatusResponseSerializer

    def get(self, request):
        return Response({'is_premium': request.user.has_active_premium(), 'premium_expires_at': request.user.premium_expires_at})


@extend_schema(
    tags=['Premium'],
    request=None,
    responses={
        200: MessageResponseSerializer,
    },
    summary="Upgrade to premium",
    description="Upgrade user account to premium (placeholder for payment)"
)
class PremiumUpgradeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        # Payment placeholder: grant 30 days
        request.user.is_premium = True
        request.user.premium_expires_at = timezone.now() + timezone.timedelta(days=30)
        request.user.save(update_fields=['is_premium', 'premium_expires_at'])
        return Response({'detail': 'Upgraded'})


@extend_schema(
    tags=['Premium'],
    request=PremiumGrantSerializer,
    responses={
        200: MessageResponseSerializer,
        404: MessageResponseSerializer,
    },
    summary="Grant premium access",
    description="Grant premium access to user (admin only)"
)
class PremiumGrantView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = PremiumGrantSerializer

    def post(self, request):
        username = request.data.get('username')
        days = int(request.data.get('days', 365))
        user = User.objects.get(username=username)
        user.is_premium = True
        user.premium_expires_at = timezone.now() + timezone.timedelta(days=days)
        user.save(update_fields=['is_premium', 'premium_expires_at'])
        return Response({'detail': 'Granted'})


@extend_schema(
    tags=['Testing'],
    request=TestEmailSerializer,
    responses={
        200: TestEmailResponseSerializer,
        500: TestEmailResponseSerializer,
    },
    summary="Send test email",
    description="Send a test email to verify email configuration"
)
class TestEmailView(APIView):
    """Test view to verify Liara email configuration"""
    permission_classes = [IsAuthenticated]
    serializer_class = TestEmailSerializer

    def post(self, request):
        serializer = TestEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'message': 'Invalid input'}, status=400)
        
        recipient_email = serializer.validated_data.get('email', request.user.email)
        subject = "Test Email from Uni Project"
        message = "This is a test email sent using Liara SMTP service. If you receive this, the email configuration is working correctly!"
        headers = {"x-liara-tag": "test-email"}  # Custom headers for Liara

        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=None,  # Uses MAIL_FROM from settings.py
                to=[recipient_email],
                headers=headers,
            )
            email.send()
            return Response({"status": "success", "message": f"Test email sent successfully to {recipient_email}!"})
        except Exception as e:
            return Response({"status": "error", "message": f"Failed to send email: {str(e)}"}, status=500)
