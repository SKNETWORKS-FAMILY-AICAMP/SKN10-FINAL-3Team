from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password=None, **extra_fields):
        if not name:
            raise ValueError("이름은 필수입니다.")
        if not email:
            raise ValueError("이메일은 필수입니다.")
        if not password:
            raise ValueError("비밀번호는 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(name, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # 필수 정보
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=255)

    # 선택 입력
    bio = models.TextField(blank=True, null=True)              # 자기소개
    exp_career = models.TextField(blank=True, null=True)       # 소속경력
    exp_activity = models.TextField(blank=True, null=True)      # 수행경력
    education_high = models.CharField(max_length=255, blank=True, null=True)   # 고등학력
    education_univ = models.CharField(max_length=255, blank=True, null=True)   # 대학 학력
    education_grad = models.CharField(max_length=255, blank=True, null=True)   # 대학원 학력

    # 참조 외래키 (on_delete 방식은 적절히 수정 가능)
    # department = models.ForeignKey('code.Organization', on_delete=models.SET_NULL, null=True, related_name='users')  # 소속부서
    # role = models.ForeignKey('code.Role', on_delete=models.SET_NULL, null=True, related_name='users')               # 역할
    # category = models.ForeignKey('code.Category', on_delete=models.SET_NULL, null=True, related_name='users')       # 전문분야

    # Django 기본 권한 필드
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 생성/수정 시간
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'custom_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
