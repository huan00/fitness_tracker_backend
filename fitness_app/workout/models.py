from django.db import models
from user.models import User

# Create your models here.


class Workout(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='workouts')
    date = models.DateField()
    distance = models.FloatField(blank=True)
    calories = models.IntegerField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    @classmethod
    def create(self, workout):
        workout = self(workout)
        workout.save()

        return workout


    def __str__(self):
        return str(self.date)


class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercises')
    body_parts = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    set_count = models.IntegerField(blank=True, default=0)
    reps = models.IntegerField(blank=True, default=0)
    weight = models.FloatField(blank=True, default=0)
    duration = models.IntegerField(blank=True, default=0)
    rest_time = models.IntegerField(blank=True, default=0)
    exercise_type = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return str(self.name)
