from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    is_authenticated = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def create_user(cls, username, email=None):
        user = User.objects.create_user(username, email, cls)
        user.save()
        return True

    def __str__(self):
      return self.first_name + ' ' + self.last_name
