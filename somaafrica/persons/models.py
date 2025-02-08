import logging
import uuid

from collections.abc import Iterable

from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    Permission,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from somaafrica.commons.validator import validate_phone_number


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


class GroupManager(models.Manager):
    """
    The manager for the auth's Group model.
    """

    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Group(UserTimeStampModel):
    guid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        related_name="group_permissions",
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = "Custom Group"
        verbose_name_plural = "Custom Groups"

    @property
    def group_members(self):
        return self.user_set.all()

    @property
    def group_permissions(self):
        qs = self.permissions.all()
        return list(
            # set(
            #     [str(perm[0]) for perm in qs.values_list("codename")]
            # )
            set(qs.values_list("codename", flat=True))  # optimized
        )

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def add_user_to_group(self, user_guid):
        try:
            group_user = User.objects.get(guid=user_guid)
            group_user.groups.add(self)
        except Exception as e:
            LOGGER.warning(str(e))
            raise

    def remove_user_from_group(self, user_guid):
        try:
            group_user = User.objects.get(guid=user_guid)
            group_user.groups.remove(self)
        except Exception as e:
            LOGGER.warning(str(e))
            raise

    def add_permissions_to_group(self, perms: list):
        try:
            permissions = Permission.objects.filter(codename__in=perms)

            if not permissions.exists():
                raise ValueError("No valid permissions found")

            self.permissions.add(*permissions)
            self.save()
        except Exception as e:
            LOGGER.exception(str(e))
            raise

    def remove_permissions_from_group(self, perms: list):
        try:
            permissions = Permission.objects.filter(codename__in=perms)

            if not permissions.exists():
                raise ValueError("No valid permissions found")

            self.permissions.remove(*permissions)
            self.save()
        except Exception as e:
            LOGGER.exception(str(e))
            raise


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


class User(AbstractBaseUser, TimeStampModel):
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
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )

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

    @property
    def user_permissions(self):
        user_groups = self.groups.all()
        perms = []

        for group in user_groups:
            perms += group.group_permissions

        return perms

    @property
    def user_groups(self):
        user_groups = self.groups.all()

        return [group.name for group in user_groups]

    def change_password(self, password):
        self.set_password(password)
        self.save()
        return self

    def has_perm(self, perm, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return perm in self.user_permissions

    def has_perms(self, perm_list, obj=None):
        if not isinstance(perm_list, Iterable) or isinstance(perm_list, str):
            LOGGER.error("perm_list must be an iterable of permissions.")
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)


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
        related_name="person",
        null=True,
        blank=True
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
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'date_of_birth'],
                name='unique_person'
            )
        ]

    def add_user(self, user: str):
        try:
            self.user = User.objects.get(guid=user)
            self.save()
        except Exception as e:
            LOGGER.exception(str(e))
            raise

    def remove_user(self):
        self.user = None
        self.save()

    def add_phone(self, phone_data):
        try:
            phone, _ = Phone.objects.get_or_create(**phone_data)
            self.phone.add(phone)
        except Exception as e:
            LOGGER.exception(str(e))
            raise

    def remove_phone(self, phone_data):
        try:
            phone = Phone.objects.get(**phone_data)
            self.phone.remove(phone)
        except Exception as e:
            LOGGER.exception(str(e))
            raise

    def add_address(self, address_data):
        try:
            address, _ = Address.objects.get_or_create(**address_data)
            self.address.add(address)
        except Exception as e:
            LOGGER.exception(str(e))
            raise

    def remove_address(self, address_data):
        try:
            address = Address.objects.get(**address_data)
            self.address.remove(address)
        except Exception as e:
            LOGGER.exception(str(e))
            raise
