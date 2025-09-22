from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Premium', {'fields': ('is_premium', 'premium_expires_at')}),
    )
    list_display = ('username', 'email', 'is_active', 'is_premium', 'premium_expires_at', 'is_staff')
