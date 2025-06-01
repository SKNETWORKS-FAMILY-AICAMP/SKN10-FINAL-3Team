# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.forms import TextInput, Textarea
from django import forms


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'email': TextInput(attrs={'size': '40'}),
            'name': TextInput(attrs={'size': '40'}),
        }

class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    model = User
    list_display = ('id', 'name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')

    fieldsets = (
        (None, {'fields': ('name', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'role')}
        ),
    )

    search_fields = ('name', 'email')
    ordering = ('id',)


admin.site.register(User, UserAdmin)
