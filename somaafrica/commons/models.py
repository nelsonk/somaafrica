from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

import phonenumbers


def validate_international_phone_number(value):
    try:
        # Parse the phone number with an optional region
        phone_number = phonenumbers.parse(value, None)

        # Validate the number
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError(f'{value} not a valid international number')

    except phonenumbers.NumberParseException:
        raise ValidationError(f'{value} is not a valid phone number format.')


class TimeStampModel(models.Model):
    """
    This is for time record was created or updated
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserTrackerModel(models.Model):
    """
    This is for user who created or updated record
    """
    created_by = models.UUIDField(editable=False)
    updated_by = models.UUIDField()

    class Meta:
        abstract = True


class UserTimeStampModel(TimeStampModel, UserTrackerModel):
    """
    This is for time and user when/who created or updated record
    """

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    """
    Customer user manager for our custom user
    """
    def create_user(self, username, email=None, password=None, **extras):
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extras)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extras):
        extras.setdefault('is_staff', True)
        extras.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extras)


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    """
    Our custom user model
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Phone(UserTimeStampModel):
    """
    Phone Model
    """
    number = models.CharField(
        max_length=20,
        validators=[validate_international_phone_number]
    )


class Address(UserTimeStampModel):
    """
    Physical address model
    """
    address = models.CharField(max_length=255)
