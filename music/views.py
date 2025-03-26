from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Artist, Song, Playlist
from .serializers import ArtistSerializer, SongSerializer, PlaylistSerializer
from .youtube_utils import search_youtube
# from .permissions import IsAdmin, IsArtist
from rest_framework.decorators import api_view, permission_classes
from oauth2_provider.models import AccessToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer


# Home View
def home(request):
    return HttpResponse("<h1>Welcome to the Music Streaming API</h1>")

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
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
    """Logout user by deleting their authentication token."""
    try:
        # Ensure the user has an authentication token
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status=200)
        return Response({"error": "User has no auth_token."}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
# Song ViewSet (for CRUD operations)
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    # permission_classes = [IsAuthenticated, IsArtist]

    def perform_create(self, serializer):
        print(self.request.data)

        artist_name = self.request.data.get("artist_name")
        if not artist_name:
            raise serializers.ValidationError({"artist_name": "Artist name is required"})
        

        """Ensure artist exists before saving song."""
        song_data = serializer.validated_data
        artist_name = song_data.pop("artist_name")

        if not artist_name:
            raise serializers.ValidationError({"artist_name": "Artist name is required"})

        # Get or create the artist instance
        artist, _ = Artist.objects.get_or_create(name=artist_name)

        # Search for a YouTube link
        song_data = serializer.validated_data
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
        artist_name = song_data.pop("artist_name")

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
