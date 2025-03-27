from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtistViewSet,
    SongViewSet,
    PlaylistViewSet,
    register,
    login,
    logout,
    home
)

router = DefaultRouter()
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'songs', SongViewSet, basename='song')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('', include(router.urls)),
]