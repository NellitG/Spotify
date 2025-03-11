from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name =models.CharField(max_length=255)
    bio = models.TextField(blank=True) #store biography of artist
    image = models.ImageField(upload_to='artists/',)

    def __str__(self):
        return self.name
    
class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    audio_url = models.FileField()
    duration = models.IntegerField(help_text="Duration of song in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)#store user who created the playlist. When user deleted playlist deleted
    name = models.CharField(max_length=255)
    songs = models. ManyToManyField(Song)

    def __str__(self):
        return self.name
