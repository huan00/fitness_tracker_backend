from rest_framework import serializers
from .models import Workout, Exercise
from user.models import User


class WorkoutSerializer(serializers.ModelSerializer):

  class Meta:
    model = Workout
    fields=('id','user_id', 'date', 'distance', 'calories', 'notes')

  def create(validated_data):
    user = validated_data.pop('user')
    user = User.objects.get(pk=user)
    workout = Workout.objects.create(**validated_data, user=user)
    return workout
  



class ExerciseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Exercise
    fields='__all__'

  def create( validated_data):
      workout = validated_data.pop('workout')
      workoutId = Workout.objects.get(pk=workout)
      exercise = Exercise.objects.create(**validated_data, workout=workoutId)

      return exercise
  
class WorkoutExerciseSerializer(serializers.ModelSerializer):
  exercises = ExerciseSerializer(many=True)

  class Meta:
    model = Workout
    fields = (
      'id',
      'user_id',
      'date',
      'distance',
      'calories',
      'notes',
      'exercises'
    )