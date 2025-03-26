from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from PIL import Image
import os
# from django.contrib.auth.models import AbstractUser

class User(User):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('artist', 'Artist'),
        ('listener', 'Listener'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='listener')

    def is_admin(self):
        return self.role == 'admin'
    
    def is_artist(self):
        return self.role == 'artist'

class Artist(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensure artist names are unique
    bio = models.TextField(blank=True)  # Store artist biography
    image = models.ImageField(upload_to='artists/', null=True, blank = True)  # Allow blank images

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            if img_path.lower().endswith(".jfif"):
                img = Image.open(img_path)
                new_path = img_path.rsplit(".", 1)[0] + ".jpg"  # Change extension
                img.convert("RGB").save(new_path, "JPEG")  # Convert to JPEG
                os.remove(img_path)  # Delete the original .jfif file
                self.image.name = self.image.name.rsplit(".", 1)[0] + ".jpg"  # Update DB
                super().save(update_fields=["image"])  # Save the model

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order artists alphabetically

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE)
    youtube_url = models.CharField(
        max_length=255, null=True, blank=True, validators=[URLValidator()]
    )
    duration = models.IntegerField(help_text="Duration of song in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # When user deleted, playlist deleted
    name = models.CharField(max_length=255)
    songs = models.ManyToManyField("Song", related_name = "playlists")

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        ordering = ['name']  # Order playlists alphabetically
