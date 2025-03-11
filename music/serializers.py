from rest_framework import serializers #built in djangorest framework
from .models import Artist, Song, Playlist

class ArtistSerializer(serializers.ModelSerializer):#serializes model instance
    class Meta: #provides metadata to the serializer class
        model = Artist
        fields = "__all__"

class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    youtube_url =serializers.CharField()

    class Meta:
        model = Song
        fields = ["id", "title", "artist", "youtube_url", "duration", "uploaded_at"]

    def validate_youtube_url(self, value):
        if not value.startswith("https://www.youtube.com/watch"):
            raise serializers.ValidationError("Invalid Youtube URL")
        return value

class PlaylistSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = "__all__"
