# models.py
from django.db import models
import random
import string


class User(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    auth_code = models.CharField(max_length=4, blank=True, null=True)
    invite_code = models.CharField(max_length=50, blank=True, null=True)

    def generate_auth_code(self):
        return ''.join(random.choices(string.digits, k=4))

    def generate_invite_code(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def __str__(self):
        return f"User(phone={self.phone_number})"
