# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from code_t.models import Code_T
from django import forms

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        org_cd = cleaned_data.get('org_cd')
        # org_cd가 ORG_01로 시작하면 cat_cd를 CAT_01로
        # org_cd가 ORG_02로 시작하면 cat_cd를 CAT_02로
        if org_cd:
            if org_cd.startswith('ORG_01'):
                cleaned_data['cat_cd'] = 'CAT_01'
            elif org_cd.startswith('ORG_02'):
                cleaned_data['cat_cd'] = 'CAT_02'
        return cleaned_data

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    model = CustomUser
    
    # 리스트에서 라벨 보여주기
    def org_label(self, obj):
        code_obj = Code_T.objects.filter(code=obj.org_cd).first()
        return code_obj.code_label if code_obj else obj.org_cd
    org_label.short_description = '부서'

    def role_label(self, obj):
        code_obj = Code_T.objects.filter(code=obj.role_cd).first()
        return code_obj.code_label if code_obj else obj.role_cd
    role_label.short_description = '역할'
    
    def cat_label(self, obj):
        code_obj = Code_T.objects.filter(code=obj.cat_cd).first()
        return code_obj.code_label if code_obj else obj.cat_cd
    cat_label.short_description = '전문분야'
    
    list_display = [
        'id', 'email', 'name', 'phone',
        'org_label', 'role_label', 'cat_label', 'is_partner',
        'is_staff', 'is_superuser', 'created_dt', 'updated_dt'
    ]
    ordering = ['id']
    list_filter = ['is_active', 'is_partner', 'is_staff', 'is_superuser']
    search_fields = ['email', 'name']

    readonly_fields = ('created_dt', 'updated_dt', 'org_label', 'role_label')

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
                'is_partner',
                'is_staff',
                'is_superuser',
            )
        }),
        ('조직 및 역할', {'fields': ('org_label', 'role_label', 'org_cd', 'role_cd', 'cat_cd')}),
        ('생성 및 수정 날짜', {'fields': ('created_dt', 'updated_dt')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2', 'is_partner', 'is_staff', 'is_superuser', 'org_cd', 'role_cd', 'cat_cd','bio', 'exp_career', 'exp_activity', 'education_high', 'education_univ', 'education_grad'),
        }),
    )

