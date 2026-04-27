from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return self.username
