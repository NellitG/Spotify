from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Artist, Song, Playlist
from .serializers import ArtistSerializer, SongSerializer, PlaylistSerializer
from .youtube_utils import search_youtube


# Home View
def home(request):
    return HttpResponse("<h1>Welcome to the Music Streaming API</h1>")


# Song ViewSet (for CRUD operations)
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def perform_create(self, serializer):
        """Ensure artist exists before saving song."""
        song_data = serializer.validated_data
        artist_name = song_data.pop("artist")

        # Get or create the artist instance
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Search for a YouTube link
        song_name = f"{song_data['title']} by {artist.name}"
        youtube_link = search_youtube(song_name)

        # Save song with artist and valid YouTube link
        serializer.save(artist=artist, youtube_url=youtube_link)

    def perform_update(self, serializer):
        """Ensure artist exists before updating song."""
        song_data = serializer.validated_data
        artist_name = song_data.pop("artist")

        # Get or create the artist instance
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Update the song with the correct artist instance
        serializer.save(artist=artist)


# Artist ViewSet (for CRUD operations)
class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


# Playlist ViewSet (for CRUD operations)
class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ensure users can only see their own playlists."""
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure a playlist is created only for the logged-in user."""
        serializer.save(user=self.request.user)


# Artist List API View
class ArtistList(generics.ListCreateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


# Song List API View
class SongList(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def perform_create(self, serializer):
        """Ensure artist exists before saving song."""
        song_data = serializer.validated_data
        artist_name = song_data.pop("artist")

        # Get or create the artist instance
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Search for a YouTube link
        song_name = f"{song_data['title']} by {artist.name}"
        youtube_link = search_youtube(song_name)

        # Save song with artist and valid YouTube link
        serializer.save(artist=artist, youtube_url=youtube_link)


# Playlist List API View
class PlaylistList(generics.ListCreateAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ensure users can only see their own playlists."""
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure a playlist is created only for the logged-in user."""
        serializer.save(user=self.request.user)
