from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        # hash input password
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name', 'age', 'sex', 'weight', 'profile_image', 'height', 'workout_days', 'goal', 
        ]
        extra_kwargs = {'password': {'write_only': True}}