import pickle

from django.contrib.auth.models import AbstractUser
from django.db import models


class YoutubeCredential(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    _credentials = models.BinaryField()

    def __str__(self):
        return self.client_id

    @property
    def get_credentials(self):
        return pickle.loads(self._credentials)


class User(AbstractUser):
   credentials = models.ManyToManyField('YoutubeCredential', null=True, related_name='credentials')
