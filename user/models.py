from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
    
# 역할 코드 정의
class Role(models.TextChoices):
    PARTNER = 'PARTNER', '파트너'            # 슈퍼유저
    SENIOR_LAWYER = 'SENIOR', '시니어 변호사'
    LAWYER = 'LAWYER', '변호사'
    PARALEGAL = 'PARALEGAL', '법률사무원'     # 위 3명은 모두 스템프유저
    
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, name, email=None, password=None, **extra_fields):
        if not name:
            raise ValueError('이름(name)은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.PARTNER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('슈퍼유저는 is_staff=True 이어야 합니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('슈퍼유저는 is_superuser=True 이어야 합니다.')

        return self.create_user(name, email, password, **extra_fields)

# 사용자 정의 모델 (Django의 AbstractUser를 확장하여 추가 정보 관리)
class User(AbstractUser):
    username = None

    name = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LAWYER,
    )

    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    @property
    def is_stamp_user(self):
        return self.role in {
            Role.SENIOR_LAWYER,
            Role.LAWYER,
            Role.PARALEGAL
        }

    @property
    def is_partner(self):
        return self.role == Role.PARTNER