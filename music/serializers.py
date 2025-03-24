import re
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Artist, Song, Playlist

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        return User.objects.create_user(**validated_data)

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)  # Serialize artist object
    artist_name = serializers.CharField(write_only=True)  # For input

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'artist_name', 'youtube_url']

    def validate_youtube_url(self, value):
        """Ensure the YouTube URL is valid."""
        youtube_pattern = re.compile(
            r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)([\w-]+)'
        )
        if not youtube_pattern.match(value):
            raise serializers.ValidationError("Invalid YouTube URL")
        return value

    def create(self, validated_data):
        """Ensure artist exists before saving song."""
        artist_name = validated_data.pop("artist_name", None)

        if not artist_name:
            raise serializers.ValidationError({"artist_name": "Artist name is required"})

        artist, _ = Artist.objects.get_or_create(name=artist_name)
        return Song.objects.create(artist=artist, **validated_data)

class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlist model, linking user and songs."""
    user = serializers.ReadOnlyField(source="user.username")
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True)

    class Meta:
        model = Playlist
        fields = "__all__"
