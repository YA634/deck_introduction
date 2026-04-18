from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin , BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='メールアドレス')
    username = models.CharField(max_length=20, blank=True, verbose_name='ユーザー名')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'  # ログイン時にemailを使用
    REQUIRED_FIELDS = []  # createsuperuserで追加で聞かれるフィールド
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'