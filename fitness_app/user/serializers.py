from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, WorkoutPreference, Program, Equipment, EquipmentList, Goal, WorkoutGoal
from workout.serializers import WorkoutExerciseSerializer

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


class ProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = (
            'id',
            'name',
        )


class WorkoutPreferenceSerializer(serializers.ModelSerializer):
    preference = ProgramSerializer(many=True)

    class Meta:
        model = WorkoutPreference
        fields = (
            'id',
            'user',
            'preference',
        )


class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = ('id', 'name')


class EquipmentListSerializer(serializers.ModelSerializer):
    equipments = EquipmentSerializer(many=True)

    class Meta:
        model = EquipmentList
        fields = ('id', 'user', 'equipments')


class GoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goal
        fields = ('id', 'goal')


class WorkoutGoalSerializer(serializers.ModelSerializer):
    goals = GoalSerializer(many=True)

    class Meta:
        model = WorkoutGoal
        fields = ('id', 'user', 'goals')


class UserFullSerializer(serializers.ModelSerializer):
    workoutPreference = WorkoutPreferenceSerializer(many=True)
    EquipmentsList = EquipmentListSerializer(many=True)
    workoutGoals = WorkoutGoalSerializer(many=True)
    workouts = WorkoutExerciseSerializer(many=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'age', 'gender', 'weight', 'profile_image', 'height', 'workoutPreference', 'EquipmentsList', 'workoutGoals', 'workouts'
        ]
