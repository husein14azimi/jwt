# account.models

from django.db import models
from django.conf import settings


gender_choices = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class Person(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)

    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}: {self.user.email}'