from rest_framework import serializers
from .models import User, SpotifyToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'firstname', 'lastname']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class SpotifyTokenSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SpotifyToken
        fields = ['user', 'access_token', 'refresh_token', 'expires_at']
