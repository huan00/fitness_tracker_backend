from django.contrib import admin
from .models import User, Program, WorkoutGoal, WorkoutPreference
# Register your models here.

admin.site.register(User)
admin.site.register(Program)
admin.site.register(WorkoutGoal)
admin.site.register(WorkoutPreference)
