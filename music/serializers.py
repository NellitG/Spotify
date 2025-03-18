#Serializers convert complex data into a simple format that can easily be shared across the network. They also validate the data before saving it to the database. In this file, we define serializers for the Artist, Song, and Playlist models.
#Think of them as serializers
import re
from rest_framework import serializers
from .models import Artist, Song, Playlist

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']  # Ensure 'name' is included

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)  # Serialize the artist object

    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'youtube_url']

    def validate_youtube_url(self, value):
        """Ensure the YouTube URL is valid."""
        youtube_pattern = re.compile(
            r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)([\w-]+)'
        )
        if not youtube_pattern.match(value):
            raise serializers.ValidationError("Invalid YouTube URL")
        return value  # Ensure return is inside the function

    def create(self, validated_data):
        """Ensure artist exists before saving song."""
        artist_name = validated_data.pop("artist", None)

        if not artist_name:
            raise serializers.ValidationError({"artist": "Artist name is required"})

        artist, _ = Artist.objects.get_or_create(name=artist_name)
        return Song.objects.create(artist=artist, **validated_data)

class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlist model, linking user and songs."""
    user = serializers.ReadOnlyField(source="user.username")
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True)

    class Meta:
        model = Playlist
        fields = "__all__"
