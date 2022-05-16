from datetime import timedelta
from random import choices
from string import digits

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from django_extensions.db.models import TimeStampedModel

from .validators import six_digits


class EmailUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(
        self, username=None, email=None, password=None, **extra_fields
    ):
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField("email address", unique=True)
    data = models.JSONField("data", default=dict, blank=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    objects = EmailUserManager()

    EMAIL_FIELD = USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.get_full_name()


class OneTimeCode(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, validators=[six_digits])

    class Meta:
        verbose_name = "one-time-code"
        verbose_name_plural = "one-time-codes"

    @classmethod
    def generate(cls, user):
        return cls.objects.create(user=user, code="".join(choices(digits, k=6)))

    @classmethod
    def validate(cls, user, code):
        ten_minutes_ago = now() - timedelta(minutes=10)
        otp = get_object_or_404(cls, user=user, code=code, created__gt=ten_minutes_ago)
        user.is_active = True
        user.save()
        otp.delete()
        return user
