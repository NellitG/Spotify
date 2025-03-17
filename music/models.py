from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure artist names are unique
    bio = models.TextField(blank=True)  # Store artist biography
    image = models.ImageField(upload_to='artists/', blank=True, default='')  # Allow blank images

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order artists alphabetically

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)  # When artist deleted, songs also deleted
    youtube_url = models.URLField(max_length=255, null=True, blank=True)  # Use URLField for validation
    duration = models.IntegerField(help_text="Duration of song in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.artist.name}"

    class Meta:
        ordering = ['-uploaded_at']  # Show latest songs first

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # When user deleted, playlist deleted
    name = models.CharField(max_length=255)
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        ordering = ['name']  # Order playlists alphabetically
