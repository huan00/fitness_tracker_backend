from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, WorkoutPreference, Program


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        # hash input password
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name', 'age', 'gender', 'weight', 'profile_image', 'height',
        ]
        extra_kwargs = {'password': {'write_only': True}}


class WorkoutPreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkoutPreference

        fields = (
            'id',
            'user',
            'program',
        )


class ProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = (
            'id',
            'name',
        )
