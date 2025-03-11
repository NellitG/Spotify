from django.shortcuts import render
from rest_framework import generics
from .models import Artist, Song, Playlist
from .serializers import ArtistSerializer, SongSerializer, PlaylistSerializer
from rest_framework.permissions import IsAuthenticated
from .youtube_utils import search_youtube

class ArtistList(generics.ListCreateAPIView): #API endpoint to list all artists or add a new artist
    queryset = Artist.objects.all() #use all artists in the database
    serializer_class = ArtistSerializer #specifies the serializer that converts Artist objects to JSON(API) format

class SongList(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class PlaylistList(generics.ListCreateAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        song_data = serializer.validated_data
        song_name = f"{song_data['title']} by {song_data['artist']}"
        youtube_link = search_youtube(song_name)

        if youtube_link:
            serializer.save(youtube_url=youtube_link)