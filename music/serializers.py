import re
from rest_framework import serializers
from .models import Artist, Song, Playlist

class ArtistSerializer(serializers.ModelSerializer):
    """Serializer for Artist model."""
    class Meta:
        model = Artist
        fields = "__all__"

class SongSerializer(serializers.ModelSerializer):
    artist = serializers.CharField()  # Accept artist name as a string

    class Meta:
        model = Song
        fields = "__all__"

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
        artist_name = validated_data.pop("artist")
        artist, _ = Artist.objects.get_or_create(name=artist_name)
        return Song.objects.create(artist=artist, **validated_data)


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlist model, linking user and songs."""
    user = serializers.ReadOnlyField(source="user.username")
    songs = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), many=True
    )

    class Meta:
        model = Playlist
        fields = "__all__"
