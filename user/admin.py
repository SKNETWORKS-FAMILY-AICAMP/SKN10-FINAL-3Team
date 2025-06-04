# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'name', 'phone', 'is_staff', 'is_superuser']
    ordering = ['email'] # 이메일 기준 정렬
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('개인 정보'), {'fields': ('name', 'phone', 'bio')}),
        (_('경력 및 학력'), {
            'fields': (
                'exp_career',
                'exp_activity',
                'education_high',
                'education_univ',
                'education_grad',
            )
        }),
        (_('권한'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('중요한 날짜'), {'fields': ('last_login', 'created_dt', 'updated_dt')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2', 'is_staff', 'is_superuser', 'bio', 'exp_career', 'exp_activity', 'education_high', 'education_univ', 'education_grad'),
        }),
    )
