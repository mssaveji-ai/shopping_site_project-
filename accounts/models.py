from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    image = models.ImageField(upload_to='images/accounts',null=True,blank=True)
    email_active_code = models.CharField(max_length=100,editable=True,unique=True)
    about_user = models.TextField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return self.get_full_name
        return self.email
# Create your models here.
