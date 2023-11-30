from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from user.models import User
from .models import Workout
from datetime import date
from user.serializers import UserSerializer
from .serializers import WorkoutSerializer, ExerciseSerializer, WorkoutExerciseSerializer
# Create your views here.
import json

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_workout(request):
 
  token = request.auth
  user = User.objects.get(email=request.user).pk

  user_serializer = UserSerializer(request.user)
 

  workout_form = request.data['workout_form']
  exercises = request.data['exercises']

  
  workout_form['user']= user_serializer.data['id']
  workout_form['date'] = date.today()

  workout_serializer = WorkoutSerializer(data=workout_form)

  if workout_serializer.is_valid(raise_exception=True):
    workout = WorkoutSerializer.create(validated_data=workout_form)
    workout_serializer = WorkoutSerializer(workout)

    # create exercise in the workout and attach to workout
    warmup = exercises['warmup']
    workout = exercises['workout']
    cooldown = exercises['cooldown']

    print(cooldown)

    for exercise in warmup:
      exercise_set = {
        'workout': workout_serializer.data['id'],
        'name': exercise['name'],
        'set_count': exercise['set'] if 'set' in exercise else 0,
        'body_parts': ','.join(exercise['body_parts']),
        'reps':  exercise['rep'] if 'rep' in exercise else 0,
        'duration': exercise['duration'] if 'duration' in exercise else 0,
        'weight':  0,
        'rest_time': 0,
        'exercise_type': 'warmup'
      }
      # exercise['workout'] = workout_serializer.data['id']

      exercise_serializer = ExerciseSerializer(data=exercise_set)
      
      if exercise_serializer.is_valid(raise_exception=True):
        exercise_workout = ExerciseSerializer.create(validated_data=exercise_set)

    for exercise in workout:
      exercise_set = {
        'workout': workout_serializer.data['id'],
        'name': exercise['name'],
        'set_count': exercise['set'] if 'set' in exercise else 0,
        'body_parts': ','.join(exercise['body_parts']),
        'reps':  exercise['rep'] if 'rep' in exercise else 0,
        'duration': exercise['duration'] if 'duration' in exercise else 0,
        'weight':  0,
        'rest_time': 0,
        'exercise_type': 'workout'
      }

      exercise_serializer = ExerciseSerializer(data=exercise_set)
      
      if exercise_serializer.is_valid(raise_exception=True):
        exercise_workout = ExerciseSerializer.create(validated_data=exercise_set)

    for exercise in cooldown:
      exercise_set = {
        'workout': workout_serializer.data['id'],
        'name': exercise['name'],
        'set_count': exercise['set'] if 'set' in exercise else 0,
        'body_parts': ','.join(exercise['body_parts']),
        'reps':  exercise['rep'] if 'rep' in exercise else 0,
        'duration': exercise['duration'] if 'duration' in exercise else 0,
        'weight': 0,
        'rest_time': 0,
        'exercise_type': 'cooldown'
      }
      exercise_serializer = ExerciseSerializer(data=exercise_set)
      
      if exercise_serializer.is_valid(raise_exception=True):
        exercise_workout = ExerciseSerializer.create(validated_data=exercise_set)

    return Response(status=status.HTTP_201_CREATED)

  return Response(status=status.HTTP_400_BAD_REQUEST)
  