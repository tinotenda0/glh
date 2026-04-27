from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_customer', 'is_seller', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('User Roles', {'fields': ('is_customer', 'is_seller')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Roles', {'fields': ('is_customer', 'is_seller')}),
    )

admin.site.register(User, CustomUserAdmin)


# Register your models here.
