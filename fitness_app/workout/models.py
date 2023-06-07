from django.db import models
from user.models import User

# Create your models here.


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    distance = models.FloatField(blank=True)
    calories = models.IntegerField(blank=True, default='')
    notes = models.TextField(blank=True, default='')


class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    set_count = models.IntegerField(blank=True, default=0)
    reps = models.IntegerField(blank=True, default=0)
    weight = models.FloatField(blank=True, default=0)
    rest_time = models.DurationField(blank=True, default=0)
