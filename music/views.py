from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Artist, Song, Playlist
from .serializers import ArtistSerializer, SongSerializer, PlaylistSerializer, UserSerializer
from .youtube_utils import search_youtube

# Home View
def home(request):
    return HttpResponse("<h1>Welcome to the Music Streaming API</h1>")

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ViewSets
class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'name'
    search_fields = ['name']

    @action(detail=True, methods=['GET'])
    def songs(self, request, name=None):
        artist = self.get_object()
        songs = artist.song_set.all()
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all().select_related('artist')
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['artist__name', 'title']
    search_fields = ['title', 'artist__name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @transaction.atomic
    def perform_create(self, serializer):
        """Handle YouTube URL search during creation."""
        validated_data = serializer.validated_data
        artist = validated_data.get('artist')
        title = validated_data.get('title')

        if artist and title:
            search_query = f"{title} by {artist.name}"
            youtube_url = search_youtube(search_query)
            serializer.save(youtube_url=youtube_url)
        else:
            serializer.save()

    @action(detail=False, methods=['GET'])
    def recent(self, request):
        recent_songs = Song.objects.order_by('-uploaded_at')[:10]
        serializer = self.get_serializer(recent_songs, many=True)
        return Response(serializer.data)

class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({"error": "song_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
            playlist.songs.add(song)
            return Response({"status": "song added"}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def remove_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({"error": "song_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = Song.objects.get(pk=song_id)
            playlist.songs.remove(song)
            return Response({"status": "song removed"}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
