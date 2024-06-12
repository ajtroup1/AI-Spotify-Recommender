from django.urls import path
from .views import *

urlpatterns = [
    path('tokens', GetTokens.as_view()),
    path('flush-tokens', FlushTokens.as_view()),
    path('users', GetUsers.as_view()),
    path('user/<str:username>', GetUser.as_view()),
    path('create-user', CreateUser.as_view()),
    path('queue', QueueSong.as_view()),
    path('spotify-callback', SpotifyCallback.as_view()), 
    path('current-track/<str:username>/<str:song_id>/', CurrentTrack.as_view()),
    path('current-track/<str:username>/', CurrentTrack.as_view()),
    path('skip-song/<str:username>', SkipSong.as_view()),
    path('rewind-song/<str:username>', RewindSong.as_view()),
    path('pause-song/<str:username>', PauseSong.as_view()),
    path('play-song/<str:username>', PlaySong.as_view()),
    path('weather', GetWeatherForLocation.as_view()),
]