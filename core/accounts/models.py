from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _



class User(AbstractUser):
    name = models.CharField(max_length=50)  
    email = models.EmailField(_('email address'), unique=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name'] 
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email 
        super(User, self).save(*args, **kwargs) 

    def __str__(self):
        return f"User: {self.name or self.username} ({self.email or 'No email'})"
