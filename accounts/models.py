from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    is_manager= models.BooleanField('Is manager', default=False)
    is_waiter = models.BooleanField('Is waiter', default=False)
    is_kitchen = models.BooleanField('Is kitchen', default=False)
    is_cashier = models.BooleanField('Is cashier', default=False)