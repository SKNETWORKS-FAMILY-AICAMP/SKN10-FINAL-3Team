# user/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, phone, password=None, **extra_fields):
        if not name:
            raise ValueError("이름은 필수입니다.")
        if not email:
            raise ValueError("이메일은 필수입니다.")
        if not phone:
            raise ValueError("전화번호는 필수입니다.")
        if not password:
            raise ValueError("비밀번호는 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(name=name, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_partner(self, name, email, phone, password=None, **extra_fields):
        user = self.create_user(
            name=name,
            email=email,
            phone=phone,
            password=password,
            **extra_fields
        )
        user.is_active = True
        user.is_partner = True  # 파트너 여부
        user.is_staff = True

        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, email, phone, password=None, **extra_fields):
        user = self.create_user(
            name=name,
            email=email,
            phone=phone,
            password=password,
            **extra_fields
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser, PermissionsMixin):
    username = None  # 사용자 이름 필드 제거
    # 필수 정보
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=30)  # 역할 (예: 관리자, 사용자 등)
    
    is_active = models.BooleanField(default=True)  # 활성화 여부(사내직원)
    is_partner = models.BooleanField(default=False)  # 파트너 여부(파트너)
    is_staff = models.BooleanField(default=False)  # 관리자 페이지 접근 여부(전산팀)
    is_superuser = models.BooleanField(default=False)  # 슈퍼유저 여부(전산팀)
    
    # 선택 입력
    org_cd = models.CharField(max_length=30)  # 소속 코드
    role_cd = models.CharField(max_length=30)  # 역할 코드
    cat_cd = models.CharField(max_length=30, blank=True, null=True)  # 전문분야 코드

    bio = models.TextField(blank=True, null=True)  # 자기소개
    exp_career = models.TextField(blank=True, null=True)  # 소속경력
    exp_activity = models.TextField(blank=True, null=True)  # 수행경력
    education_high = models.CharField(max_length=255, blank=True, null=True)  # 고등학력
    education_univ = models.CharField(max_length=255, blank=True, null=True)  # 대학 학력
    education_grad = models.CharField(max_length=255, blank=True, null=True)  # 대학원 학력

    # 생성/수정 시간
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    objects = CustomUserManager()

    class Meta:
        db_table = 'custom_user'
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"
