import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
from .models import SpotifyToken
from django.utils import timezone
from django.db import connection

# AUTHENTICATION
def get_spotify_oauth():
    return SpotifyOAuth(
        client_id='bc461021081c4e85bf4beecb4444c1ac',
        client_secret='e2d2f8d640fe4c5cbe210afb6540a420',
        redirect_uri='http://127.0.0.1:8000/api/spotify-callback',
        scope='user-library-read playlist-modify-public user-modify-playback-state user-read-currently-playing user-read-playback-state'
    )

def is_authenticated(user):
    token = SpotifyToken.objects.filter(user=user).first()
    if token:
        if timezone.now() > token.expires_at:
            refresh_token(user)

        return True
    return False

def authenticate_user(username):
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url(state=username)
    return auth_url

def save_tokens(user, token_info):
    expires_at = timezone.now() + timedelta(seconds=token_info['expires_in'])
    SpotifyToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'expires_at': expires_at
        }
    )

def refresh_token(user):
    token = SpotifyToken.objects.filter(user=user).first()
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.refresh_access_token(token.refresh_token)
    save_tokens(user, token_info)

def get_spotify_client(user):
    token = SpotifyToken.objects.filter(user=user).first()
    sp = spotipy.Spotify(auth=token.access_token)
    return sp

# RECOMMENDATIONS

# MANIPULATE PLAYBACK
