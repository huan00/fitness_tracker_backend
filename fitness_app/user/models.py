
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

import os

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('You did not provided a valid email')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self._create_user(email, password, **extra_fields)


def upload_path(instance, filename):
    if instance:
        return '/'.join(['profile', filename])
    return None


class User(AbstractBaseUser, PermissionsMixin):
    GOAL_CHOICES = [(
        'A', 'Staying Healthy'), ('B', 'Lose Weight'), ('C', 'Tone Muscle'), ('D', 'Gain Muscle')]

    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=upload_path, default='', blank=True)
    height = models.IntegerField(blank=True, null=True)
    workout_days = models.IntegerField(default=0, blank=True)
    goal = models.CharField(default = 'A', choices= GOAL_CHOICES)
    PR_history = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email',
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email.split('@')[0]
