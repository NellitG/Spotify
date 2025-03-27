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
        return User.objects.create_user(**validated_data)

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'image']
        read_only_fields = ['id']

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_name = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Name of the artist (required for creation/update)"
    )

    class Meta:
        model = Song
        fields = [
            'id', 
            'title', 
            'artist', 
            'artist_name', 
            'youtube_url', 
            'duration', 
            'uploaded_at'
        ]
        read_only_fields = ['id', 'youtube_url', 'uploaded_at', 'artist']

    def validate_artist_name(self, value):
        """Validate and clean the artist name."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Artist name cannot be empty")
        return value

    def validate_youtube_url(self, value):
        """Validate YouTube URL format if provided."""
        if value:  # Only validate if URL is provided
            youtube_pattern = re.compile(
                r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)([\w-]+)'
            )
            if not youtube_pattern.match(value):
                raise serializers.ValidationError("Invalid YouTube URL format")
        return value

    def create(self, validated_data):
        """Create song with artist from artist_name."""
        artist_name = validated_data.pop('artist_name')
        artist, _ = Artist.objects.get_or_create(name=artist_name)
        
        # Create song with the artist
        song = Song.objects.create(artist=artist, **validated_data)
        return song

    def update(self, instance, validated_data):
        """Update song including artist if artist_name provided."""
        if 'artist_name' in validated_data:
            artist_name = validated_data.pop('artist_name')
            artist, _ = Artist.objects.get_or_create(name=artist_name)
            instance.artist = artist
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        """Include artist_name in the output for convenience."""
        representation = super().to_representation(instance)
        representation['artist_name'] = instance.artist.name
        return representation

class PlaylistSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    songs = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), 
        many=True,
        required=False
    )

    class Meta:
        model = Playlist
        fields = ['id', 'user', 'name', 'songs', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def to_representation(self, instance):
        """Include full song objects instead of just IDs."""
        representation = super().to_representation(instance)
        representation['songs'] = SongSerializer(
            instance.songs.all(), 
            many=True
        ).data
        return representation