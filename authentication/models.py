from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
import uuid
from .manager import UserManager

class AppUser(AbstractBaseUser, PermissionsMixin):
    public_id = models.UUIDField(unique=True, editable=False, db_index=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    objects = UserManager()




