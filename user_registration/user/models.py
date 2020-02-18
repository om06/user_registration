from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.exceptions import ValidationError

from . import Constants

__author__ = "Hariom"


class State(models.Model):
    name = models.CharField(max_length=Constants.NAME_MAX_LENGTH, help_text="State name")
    short_name = models.CharField(max_length=Constants.SHORT_LENGTH, help_text="Code for state")

    def __str__(self):
        return self.name

    def clean(self):
        if not len(self.short_name) >= 2:
            raise ValidationError("State short length should be greater than equal to 2")


class District(models.Model):
    name  = models.CharField(max_length=Constants.NAME_MAX_LENGTH, help_text="District name")
    state = models.ForeignKey(State, related_name="districts", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def clean(self):
        if not len(self.name) > 3:
            raise ValidationError("District length should be greater than 3")


class SubDistrict(models.Model):
    name     = models.CharField(max_length=Constants.NAME_MAX_LENGTH, help_text="Sub-district name")
    district = models.ForeignKey(District, related_name="subdistricts", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Village(models.Model):
    name = models.CharField(max_length=Constants.NAME_MAX_LENGTH, help_text="Village name")
    sub_district = models.ForeignKey(SubDistrict, related_name="villages", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(
            self, username, password=None, is_staff=False, is_active=True,
            **extra_fields):
        """Create a user instance with the given email and password."""

        user = self.model(
            username=username, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user


class User(PermissionsMixin, AbstractBaseUser):
    username            = models.CharField(max_length=Constants.NAME_MAX_LENGTH, unique=True)
    registration_number = models.CharField(max_length=Constants.REG_MAX_LENGTH, blank=True, null=True)
    is_active           = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'


class Address(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    state    = models.ForeignKey(State, related_name="addresses", on_delete=models.PROTECT)
    district = models.ForeignKey(District, related_name="addresses", on_delete=models.PROTECT)
    sub_district = models.ForeignKey(SubDistrict, related_name="addresses", on_delete=models.PROTECT)
    village      = models.ForeignKey(Village, related_name="addresses", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user} - {self.village}, {self.sub_district} - {self.district}({self.state.short_name0})"

    def get_user_registration_id(self):
        state_code    = self.state.short_name[:2]
        district_code = self.district.name[:3]
        user_code     = str(self.user.pk).zfill(6)
        return f"{state_code}{district_code}{user_code}".upper()

    def set_user_registration_code(self):
        self.user.registration_number = self.get_user_registration_id()
        self.user.save()
