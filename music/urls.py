from django.urls import path
from .views import ArtistList, SongList, PlaylistList

urlpatterns = [
    path("artists/", ArtistList.as_view(), name="artist-list"),
    path("songs/", SongList.as_view(), name="song-list"),
    path("playlists/", PlaylistList.as_view(), name="playlist-list"),
]
