from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import hashlib
import secrets


class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)

    def has_active_premium(self) -> bool:
        return bool(self.is_premium and self.premium_expires_at and self.premium_expires_at > timezone.now())


class EmailVerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def create_for_user(cls, user, code: str, ttl_minutes: int = 30):
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return cls.objects.create(
            user=user,
            code_hash=code_hash,
            expires_at=timezone.now() + timezone.timedelta(minutes=ttl_minutes),
        )

    @classmethod
    def verify_code(cls, user, code: str) -> bool:
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        obj = (
            cls.objects.filter(user=user, code_hash=code_hash, expires_at__gt=timezone.now())
            .order_by('-created_at')
            .first()
        )
        if obj:
            obj.delete()
            return True
        return False


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    @classmethod
    def create_for_user(cls, user, ttl_minutes: int = 30):
        raw = f"{secrets.randbelow(1000000):06d}"
        code_hash = hashlib.sha256(raw.encode()).hexdigest()
        obj = cls.objects.create(
            user=user,
            code_hash=code_hash,
            expires_at=timezone.now() + timezone.timedelta(minutes=ttl_minutes),
        )
        obj.raw_code = raw
        return obj

    @classmethod
    def consume_code(cls, user, raw_code: str) -> bool:
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        obj = (
            cls.objects.filter(
                user=user,
                code_hash=code_hash,
                expires_at__gt=timezone.now(),
                used=False,
            )
            .order_by('-created_at')
            .first()
        )
        if obj:
            obj.used = True
            obj.save(update_fields=['used'])
            return True
        return False

    @classmethod
    def find_user_by_code(cls, raw_code: str):
        """Find user by reset code without knowing username"""
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        obj = (
            cls.objects.filter(
                code_hash=code_hash,
                expires_at__gt=timezone.now(),
                used=False,
            )
            .order_by('-created_at')
            .first()
        )
        return obj.user if obj else None

    @classmethod
    def consume_code_by_code(cls, raw_code: str) -> tuple[bool, object]:
        """Find user and consume code in one operation"""
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        obj = (
            cls.objects.filter(
                code_hash=code_hash,
                expires_at__gt=timezone.now(),
                used=False,
            )
            .order_by('-created_at')
            .first()
        )
        if obj:
            obj.used = True
            obj.save(update_fields=['used'])
            return True, obj.user
        return False, None
