
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


import os

# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('You did not provided a valid email')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self._create_user(email, password, **extra_fields)


def upload_path(instance, filename):
    if instance:
        return '/'.join(['profile', filename])
    return None


class User(AbstractBaseUser, PermissionsMixin):
    GOAL_CHOICES = [(
        'A', 'Staying Healthy'), ('B', 'Lose Weight'), ('C', 'Tone Muscle'), ('D', 'Gain Muscle')]
    WORKOUT_PROGRAM = [
        ('A', 'Aerobic'),
        ('B', 'Strength Training'),
        ('C', 'Yoga'),
        ('D', 'Flexibility Training'),
        ('E', 'Balance Training'),
        ('F', 'Interval Training'),
        ('G', 'CrossFit'),
        ('H', 'Pilates'),
        ('I', 'Any')
    ]

    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(blank=True, null=True, max_length=10)
    weight = models.IntegerField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=upload_path, default='', blank=True)
    height = models.JSONField(default=dict, blank=True)
    # workout_days = models.IntegerField(default=0, blank=True)
    # WorkoutPreference = models.CharField(
    #     max_length=100, default='Any')
    # goal = models.CharField(default='A', choices=GOAL_CHOICES, max_length=1)
    # PR_history = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email',
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email.split('@')[0]


class WorkoutPreference(models.Model):
    # name = models.CharField(max_length=255)
    preference = models.ManyToManyField('Program')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='workoutPreference')

    class Meta:
        verbose_name = 'Workout'
        verbose_name_plural = 'Workouts'

    @classmethod
    def create(self, programs, user):
        preference = self(user=user)
        preference.save()

        for program in programs:
            preference.preference.add(program['id'])

        return preference

    def __str__(self):
        return 'Workout Preference'


class Program(models.Model):
    name = models.CharField(max_length=255)

    @classmethod
    def create(self, name):
        program = self(name=name)
        program.save()
        return program

    @classmethod
    def userProgram(self, programs):
        result = []
        for program in programs:
            try:
                programExist = Program.objects.get(name=program)
                result.append(programExist)
            except ObjectDoesNotExist:
                newProgram = Program.create(name=program)
                result.append(newProgram)

        return result

    def __str__(self):
        return self.name


class EquipmentList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='EquipmentsList')
    equipments = models.ManyToManyField('Equipment')

    class Meta:
        verbose_name = 'equipment_list'
        verbose_name_plural = 'equipment_lists'

    @classmethod
    def create(self, equipmentList, user):
        equipments = self(user=user)
        equipments.save()

        print('hello')

        for equipment in equipmentList:
            equipments.equipments.add(equipment['id'])

        return equipments

    def __str__(self):
        return 'equipment list'


class Equipment(models.Model):
    name = models.CharField(max_length=255)

    @classmethod
    def create(self, name):
        equipment = self(name=name)
        equipment.save()

        return equipment

    @classmethod
    def userEquipment(self, equipments):
        equipmentList = []
        for equipment in equipments:
            try:
                equipmentExist = Equipment.objects.get(name=equipment)
                equipmentList.append(equipmentExist)
            except ObjectDoesNotExist:
                newEquipment = Equipment.create(name=equipment)
                equipmentList.append(newEquipment)

        return equipmentList

    def __str__(self):
        return self.name


class WorkoutGoal(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='workoutGoals')
    goals = models.ManyToManyField('Goal')

    class Meta:
        verbose_name = 'goal'
        verbose_name_plural = 'goals'

    @classmethod
    def create(self, goalList, user):
        goals = self(user=user)
        goals.save()

        for goal in goalList:
            goals.goals.add(goal['id'])

        return goals

    def __str__(self):
        return 'goal'


class Goal(models.Model):
    goal = models.CharField(max_length=255)

    @classmethod
    def create(self, goal):
        goal = self(goal=goal)
        goal.save()

        return goal

    @classmethod
    def userGoal(self, goals):
        goalList = []
        for goal in goals:
            try:
                goalExist = Goal.objects.get(goal=goal)
                goalList.append(goalExist)
            except ObjectDoesNotExist:
                newGoal = Goal.create(goal=goal)
                goalList.append(newGoal)

        return goalList

    def __str__(self):
        return self.goal
