from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings

class User(AbstractUser):
    name = models.CharField(max_length=50)  
    email = models.EmailField(_('email address'), unique=True)  
    is_admin = models.BooleanField(default=False)
    admin_api_key = models.UUIDField(null=True, blank=True, unique=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email 
        super(User, self).save(*args, **kwargs) 
        
        if self.is_admin and not self.admin_api_key:
            self.create_api_key()

    def create_api_key(self):
        """ Creates an API key for the user if they are admin """
        api_key, created = APIKey.objects.get_or_create(user=self)
        if created:
            self.admin_api_key = api_key.key
            self.save(update_fields=['admin_api_key'])

    def __str__(self):
        return f"User: {self.name or self.username} ({self.email or 'No email'})"

class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  

    def __str__(self):
        return f"API Key for {self.user.email}" 
