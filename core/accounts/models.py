from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

class User(AbstractUser):
    name = models.CharField(max_length=50)  
    email = models.EmailField(_('email address'), unique=True)  
    is_admin = models.BooleanField(default=False)
    admin_api_key = models.UUIDField(null=True, blank=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email 
        super(User, self).save(*args, **kwargs) 

    def __str__(self):
        return f"User: {self.name or self.username} ({self.email or 'No email'})"

class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  

    def __str__(self):
        return f"API Key for {self.user.email}" 

@receiver(post_save, sender=User)  
def create_admin_apikey(sender, instance, created, **kwargs):
    """ Create an API key only when a new admin user is created """
    if created and instance.is_admin:  
        api_key = APIKey.objects.create(user=instance)
        instance.admin_api_key = api_key.key  
        instance.save(update_fields=["admin_api_key"])  

@receiver(pre_save, sender=User)
def create_api_key_on_promotion(sender, instance, **kwargs):
    """ Remove old API key and assign a new one when a user is promoted to admin """
    if instance.pk :
        old_instance = sender.objects.get(pk=instance.pk)
        if not old_instance.is_admin and instance.is_admin:  
            APIKey.objects.filter(user=instance).delete()
            
            new_api_key = APIKey.objects.create(user=instance)
            instance.admin_api_key = new_api_key.key  
