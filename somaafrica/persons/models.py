import uuid
import logging

from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
    Group as AuthGroup
)
from django.db import models

from somaafrica.commons.phone_validator import validate_phone_number


LOGGER = logging.getLogger(__name__)

gender_choices = [("M", "Male"), ("F", "Female")]
status_choices = [("Incomplete", "Incomplete"), ("Complete", "Complete")]


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
    def create_user(self, username=None, email=None, password=None, **extras):
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extras)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            username=None,
            email=None,
            password=None,
            **extras):
        extras.setdefault('is_staff', True)
        extras.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extras)


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    """
    Our custom user model
    """
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    username = models.CharField(max_length=150, unique=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        permissions = [
            ("modify_other_user", "Can modify other user"),
            ("delete_other_user", "Can delete other User"),
            ("delete_own_user", "Can delete own user recrord"),
            ("add_user_to_group", "Can add user to group"),
            ("remove_user_group", "Can remove user from group")
        ]

    def __str__(self):
        return f"{self.guid} - {self.username} - {self.email}"

    def change_password(self, password):
        self.set_password(password)
        self.save()
        return self


class Group(UserTimeStampModel, AuthGroup):
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        verbose_name = "Custom Group"
        verbose_name_plural = "Custom Groups"

    def add_user_to_group(self, user_guid):
        try:
            group_user = User.objects.get(guid=user_guid)
            group_user.groups.add(self)
        except Exception as e:
            LOGGER.warning(str(e))
            raise

    @property
    def group_members(self):
        return self.user_set.all()


class Phone(UserTimeStampModel):
    """
    Phone Model
    """
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    number = models.CharField(
        max_length=20,
        validators=[validate_phone_number]
    )


class Address(UserTimeStampModel):
    """
    Physical address model
    """
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    address = models.CharField(max_length=255)


class Person(UserTimeStampModel):
    """
    Person info model
    """
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="person"
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    gender = models.CharField(choices=gender_choices, null=True, max_length=1)
    date_of_birth = models.DateField(db_comment="DOB")
    phone = models.ManyToManyField(Phone, related_name="person")
    address = models.ManyToManyField(Address, related_name="person")
    account_status = models.CharField(choices=status_choices, max_length=10)

    class Meta:
        permissions = [
            ("modify_other_person", "Can modify other person"),
            ("delete_other_person", "Can delete other person"),
            ("delete_own_person", "Can delete own person record")
        ]
