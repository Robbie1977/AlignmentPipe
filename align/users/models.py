from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    is_authenticated = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True)

    def create_user(cls, username, email=None):
        user = User.objects(username, email, cls)
        user.save()
        return True
    def is_authenticated(self):
        if self.is_active == True:
          return True
        else:
          return False

    def __str__(self):
      return self.first_name + ' ' + self.last_name
