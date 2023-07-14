from django.shortcuts import render
from django.http import JsonResponse,  HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.decorators import login_required
from pydantic import Field, validator, BaseModel
import datetime
from django.utils.timezone import now
from user.models import User
from user.serializers import UserFullSerializer
from typing import Optional
from dotenv import load_dotenv

import pydantic_chatcompletion

import re
import os
import openai

import json

load_dotenv()

# os.environ['OPENAI_API_KEY'] = apikey


api_key = os.environ.get('API_KEY')
# print(os.environ)
# Create your views here.

model_name = 'text-davinci-003'
temperature = 0.0
openai.api_key = api_key
# model = OpenAI(model_name=model_name, temperature=temperature, max_tokens=2000)


class Exercise(BaseModel):
    name: str
    body_parts: list[str]
    set: int
    rep: Optional[int]
    duration: Optional[int]
    rest_duration: Optional[int]


class HIITExercise(BaseModel):
    name: str
    body_parts: list[str]
    exercise_type: str
    duration: int
    rest_time: int


class HIITWorkoutFormat(BaseModel):
    # date: datetime.now().date()
    number_set: int
    exercises: list[HIITExercise]


class WorkoutFormat(BaseModel):
    warmup: list[Exercise]
    workout: list[Exercise]
    cooldown: list[Exercise]


# llm = OpenAI(temperature = temperature)

# @csrf_protect
# @csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def getWorkout(request):
    workoutLevel, workoutTime, workoutEquipment, muscleGroup = request.data.items()

    user_email = Token.objects.get(key=request.auth).user

    def convertData(data):

        result = []
        for execise in data:
            result.append(execise.dict())

        return result

    user = User.objects.get(email=user_email)

    userSerializer = UserFullSerializer(user)

    goals = userSerializer.data['workoutGoals'][0]['goals']

    user_goals = []
    for goal in goals:
        user_goals.append(goal['goal'])

    user_equipments = []
    for equipment in userSerializer.data['EquipmentsList'][0]['equipments']:
        user_equipments.append(equipment['name'])

    user_preference = []
    for preference in userSerializer.data['workoutPreference'][0]['preference']:
        user_preference.append(preference['name'])

    messages = [{'role': 'user',
                 'content': f"""As an experienced personal trainer, develop a personalized and comprehensive workout of the day for your client, taking into account the following aspects:
                 Fitness goals: {user_goals}.
                 Experience level: {workoutLevel[1]}.
                 Exercise frequency: 3 days a week.
                 Equipment access: {user_equipments}.
                 personal preference: {user_preference}.
                 workout muscle: {muscleGroup[1]}
                 Task Requirements:
                 understand the clients fitness goals, experience level, and personal preferences.
                 design a workout of the day that last {workoutTime[1]} minutes to help the client reach their fitness goal.
                 warmup should have no rest duration.
                 provide each exercise with approppriate set count, (rep counts or duration), and rest duration if needed.
                 """}]

    # print(messages)

    instance_of_my_data = pydantic_chatcompletion.create(
        messages, WorkoutFormat, model='gpt-3.5-turbo')

    data = {'date': datetime.date.today()}
    data['warmup'] = convertData(instance_of_my_data.warmup)
    data['workout'] = convertData(instance_of_my_data.workout)
    data['cooldown'] = convertData(instance_of_my_data.cooldown)

    return JsonResponse(data, safe=False)

    # return HttpResponse('messages')
