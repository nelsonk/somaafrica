import uuid

from django.contrib.auth.models import User, Group
from django.db import models


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserTrackerModel(models.Model):
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    class Meta:
        abstract = True


class Person(TimeStampModel, UserTrackerModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="person"
    )  # noqa
    groups = models.ManyToManyField(Group, related_name="person")
    phone_number = models.CharField(max_length=15, null=True)
    gender_choices = [(1, "Male"), (2, "Female")]
    gender = models.IntegerField(choices=gender_choices, null=True)
    date_of_birth = models.DateField(null=True)
    physical_address = models.CharField(max_length=255, null=True)
    status_choices = [(1, "Incomplete"), (2, "Complete")]
    account_status = models.IntegerField(choices=status_choices)
