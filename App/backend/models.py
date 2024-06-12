from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20, null=False)
    password = models.CharField(max_length=40, null=False)
    firstname = models.CharField(max_length=250, null=False)
    lastname = models.CharField(max_length=250, null=False)


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.user.username
    
class QueueItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_uri = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.track_uri}"