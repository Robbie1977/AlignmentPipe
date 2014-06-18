from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    is_authenticated = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
      return self.name
