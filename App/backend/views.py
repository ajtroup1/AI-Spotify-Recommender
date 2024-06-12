from django.shortcuts import render
from .spotipyscripts import *
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import requests
from django.http import JsonResponse
from tensorflow.keras.models import load_model
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import pandas as pd
import tensorflow as tf
import joblib
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
from .models import SpotifyToken
from django.utils import timezone


# AI
def predict_genre(time_str, weather, mood):
    # Load the model and encoders
    model = load_model('./backend/aitools/genre_aimodel.keras')
    onehot_encoder = joblib.load('./backend/aitools/onehot_encoder.pkl')
    label_encoder = joblib.load('./backend/aitools/label_encoder.pkl')

    categorical_features = ['time_of_day', 'weather', 'mood']

    # Transform the categorical features
    input_data = pd.DataFrame([[time_str, weather, mood]], columns=categorical_features)
    input_data_encoded = onehot_encoder.transform(input_data)

    # Make prediction
    prediction = model.predict(input_data_encoded)

    # Inverse transform the prediction
    genre = label_encoder.inverse_transform([tf.argmax(prediction, axis=1).numpy()[0]])

    return genre[0]

# TOKENS
class GetTokens(APIView):
    def get(self, request):
        tokens = SpotifyToken.objects.all()
        serializer = SpotifyTokenSerializer(tokens, many=True)
        
        return Response({"Tokens": serializer.data}, status=status.HTTP_200_OK)
    
class FlushTokens(APIView):
    def post(self, request):
        tokens = SpotifyToken.objects.all()
        tokens.delete()
        
        return Response({"message": "Flushed tokens"}, status=status.HTTP_200_OK)

# USER
class GetUsers(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        
        return Response({"Users": serializer.data}, status=status.HTTP_200_OK)

class GetUser(APIView):
    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        serializer = UserSerializer(user)
        if not user:
            
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        return Response({"User": serializer.data}, status=status.HTTP_200_OK)
    
class CreateUser(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')

        user = User(username=username, password=password, firstname=firstname, lastname=lastname)

        user.save()
        
        return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)

class SpotifyCallback(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        if not code:
            
            return JsonResponse({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)

        sp_oauth = get_spotify_oauth()

        try:
            # Exchange authorization code for access token
            token_info = sp_oauth.get_access_token(code)
        except Exception as e:
            
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user associated with this state parameter (username)
        user = User.objects.filter(username=state).first()
        
        if not user:
            
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Save tokens in the database
        save_tokens(user, token_info)
        

        return JsonResponse({'message': 'Authentication successful. You can now queue songs.'}, status=status.HTTP_200_OK)
    
# SPOTIPY
class QueueSong(APIView):
    def post(self, request):
        username = request.data.get('username')
        weather = request.data.get('weather')
        mood = request.data.get('mood')
        time = timezone.now().hour

        print(f'received data:\nweather: {weather}, mood: {mood}, time: {time}')

        if 0 <= time < 12:
            time_str = "morning"
        elif 12 <= time < 18:
            time_str = "afternoon"
        else:
            time_str = "night"

        genre = predict_genre(weather=weather, mood=mood, time_str=time_str)
        print("Queueing song: ",genre)

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not is_authenticated(user):
            auth_url = authenticate_user(username)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        refresh_token(user)
        sp = get_spotify_client(user)

        try:
            recs = sp.recommendations(seed_genres=[genre], limit=1, country="US")
        except Exception as e:
            return Response({'error': 'Failed to get recommendations: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not recs['tracks']:
            return Response({'error': 'No recommendations found'}, status=status.HTTP_404_NOT_FOUND)

        track_uri = recs['tracks'][0]['uri']

        try:
            # Check if the song is already in the queue
            if QueueItem.objects.filter(user=user, track_uri=track_uri).exists():
                return Response({'error': 'Song already in queue'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Add the song to the Spotify queue
            sp.add_to_queue(uri=track_uri)
            
            # Add the song to the application's queue
            QueueItem.objects.create(user=user, track_uri=track_uri)
        except Exception as e:
            return Response({'error': 'Failed to add to queue: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            song = sp.track(track_id=track_uri)
        except Exception as e:
            return Response({'error': 'Failed to get track details: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({f'song': song}, status=status.HTTP_200_OK)

        
class CurrentTrack(APIView):
    def get(self, request, username, song_id=None):
        count = 0
        user = User.objects.filter(username=username).first()
        token = SpotifyToken.objects.filter(user=user).first()

        if not token:
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        if not user:
            print('API calls for request:', count)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if token:
            print(token.expires_at)
            if timezone.now() > token.expires_at:
                count += 1
                refresh_token(user)
        count += 1
        sp = get_spotify_client(user)

        count += 1
        if not is_authenticated(user):
            count += 1
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)
        

        try:
            count += 1
            track_info = sp.current_playback()
            if track_info is None:
                print('API calls for request:', count)
                return Response({"message": "No song"}, status=status.HTTP_404_NOT_FOUND)
            
            track_id = track_info.get('item', {}).get('uri')
            
            if song_id is not None and track_id == song_id:
                print('API calls for request:', count)
                return Response({"message": "Same song"}, status=status.HTTP_204_NO_CONTENT)
            
            artist_ids = [artist['id'] for artist in track_info['item']['artists']]
            artists_info = sp.artists(artist_ids)['artists']
            count += 1
            
            return_data = {
                "artists": artists_info,
                "track": track_info
            }
            
            print('API calls for request:', count)
            return Response(return_data, status=status.HTTP_200_OK)
        except Exception as e:
            print('API calls for request:', count)
            return Response({'error': str(e)})
        
# Controller
        
class SkipSong(APIView):
    def post(self, request, username):
        count = 0
        user = User.objects.filter(username=username).first()

        if not user:
            print('API calls for request:', count)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = SpotifyToken.objects.filter(user=user).first()

        if not token:
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        if timezone.now() > token.expires_at:
            count += 1
            refresh_token(user)

        sp = get_spotify_client(user)

        try:
            sp.next_track()
            print('API calls for request:', count)
            return Response({'message': 'Track skipped'}, status=status.HTTP_200_OK)
        except Exception as e:
            print('API calls for request:', count)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RewindSong(APIView):
    def post(self, request, username):
        count = 0
        user = User.objects.filter(username=username).first()

        if not user:
            print('API calls for request:', count)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = SpotifyToken.objects.filter(user=user).first()

        if not token:
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        if timezone.now() > token.expires_at:
            count += 1
            refresh_token(user)

        sp = get_spotify_client(user)

        try:
            sp.previous_track()
            print('API calls for request:', count)
            return Response({'message': 'Track rewinded'}, status=status.HTTP_200_OK)
        except Exception as e:
            print('API calls for request:', count)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PauseSong(APIView):
    def post(self, request, username):
        count = 0
        user = User.objects.filter(username=username).first()

        if not user:
            print('API calls for request:', count)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = SpotifyToken.objects.filter(user=user).first()

        if not token:
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        if timezone.now() > token.expires_at:
            count += 1
            refresh_token(user)

        sp = get_spotify_client(user)

        try:
            sp.pause_playback()
            print('API calls for request:', count)
            return Response({'message': 'Track paused'}, status=status.HTTP_200_OK)
        except Exception as e:
            print('API calls for request:', count)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PlaySong(APIView):
    def post(self, request, username):
        count = 0
        user = User.objects.filter(username=username).first()

        if not user:
            print('API calls for request:', count)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = SpotifyToken.objects.filter(user=user).first()

        if not token:
            auth_url = authenticate_user(username)
            print('API calls for request:', count)
            return Response({'auth_url': auth_url}, status=status.HTTP_401_UNAUTHORIZED)

        if timezone.now() > token.expires_at:
            count += 1
            refresh_token(user)

        sp = get_spotify_client(user)

        try:
            sp.start_playback()
            print('API calls for request:', count)
            return Response({'message': 'Track resuming'}, status=status.HTTP_200_OK)
        except Exception as e:
            print('API calls for request:', count)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# WEATHER

WEATHER_API_KEY = 'ec7db2bbc1c24c55933201843241405'
BASE_URL = 'http://api.weatherapi.com/v1/'

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Function to get the location based on IP address
def get_location_by_ip(ip):
    GEOLOCATION_API_URL = f'http://ip-api.com/json/{ip}'
    response = requests.get(GEOLOCATION_API_URL)
    if response.status_code == 200:
        location_data = response.json()
        city = location_data.get('city')
        region = location_data.get('regionName')
        country = location_data.get('country')
        return f"{city}, {region}, {country}"
    else:
        return None

class GetWeatherForLocation(APIView):
    def get(self, request):
        ip = get_client_ip(request)
        location = get_location_by_ip(ip)
        location = "Madison, Alabama"
        
        if not location:
            return Response({"Error": "Failed to determine location from IP address"}, status=status.HTTP_400_BAD_REQUEST)

        params = {
            "key": WEATHER_API_KEY,
            "q": location
        }

        endpoint = 'current.json'
        response = requests.post(BASE_URL + endpoint, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            loc_data = weather_data['location']
            curr_data = weather_data['current']
            desc = curr_data['condition'].get('text')
            # Define broader categories based on keywords
            text = ""
            if "CLOUDY" in desc.upper() or "OVERCAST" in desc.upper():
                text = "CLOUDY"
            elif "CLEAR" in desc.upper():
                text = "CLEAR"
            elif "SUNNY" in desc.upper():
                text = "SUNNY"
            elif "RAIN" in desc.upper() or "SHOWER" in desc.upper():
                text = "RAIN"
            elif "FOG" in desc.upper() or "MIST" in desc.upper():
                text = "FOG"
            elif "SNOW" in desc.upper():
                text = "SNOW"
            elif "STORM" in desc.upper():
                text = "STORM"
            else:
                text = "OTHER"
            data = {
                "name": loc_data.get('name'),
                "region": loc_data.get('region'),
                "country": loc_data.get('country'),
                "temp_f": curr_data.get('temp_f'),
                "is_day": curr_data.get('is_day'),
                "condition": text,
                "precip": curr_data.get('precip_in'),
                "humidity": curr_data.get('humidity')
            }

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "Failed to fetch weather data"}, status=response.status_code)