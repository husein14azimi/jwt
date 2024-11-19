# core.models

from django.db import models
from django.contrib.auth.models import AbstractUser  as BaseAbstractUser 
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        """Create and return a 'User' with an email, phone number and password."""
        if not email:
            raise ValueError('The Email field must be set')
        if not phone_number:
            raise ValueError('The Phone number field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)  # Use set_password to hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        """Create and return a superuser with an email, phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, password, **extra_fields)
    

class User(BaseAbstractUser ):
    username = models.CharField(max_length=255, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^09\d{9}$', message="Phone number must start with 09 and be exactly 11 characters.")
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['phone_number']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.email}'