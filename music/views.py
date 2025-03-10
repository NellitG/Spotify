from django.shortcuts import render
from rest_framework import generics
from .models import Artist, Song, Playlist
from .serializers import ArtistSerializer, SongSerializer, PlaylistSerializer
from rest_framework.permissions import IsAuthenticated

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
        serializer.save(user=self.request.user)