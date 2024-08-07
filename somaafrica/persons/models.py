import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from somaafrica.commons.models import UserTimeStampModel, Phone, Address


gender_choices = [("M", "Male"), ("F", "Female")]
status_choices = [("Incomplete", "Incomplete"), ("Complete", "Complete")]


class Person(UserTimeStampModel):
    """
    Person info model
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4(),
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="person"
    )
    groups = models.ManyToManyField(Group, related_name="person")
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    gender = models.CharField(choices=gender_choices, null=True, max_length=1)
    date_of_birth = models.DateField(db_comment="DOB")
    phone = models.ManyToManyField(Phone, related_name="person")
    address = models.ManyToManyField(Address, related_name="person")
    account_status = models.CharField(choices=status_choices, max_length=10)
