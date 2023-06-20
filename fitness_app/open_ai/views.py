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
from datetime import date
from django.utils.timezone import now
from user.models import User
from user.serializers import UserFullSerializer

import pydantic_chatcompletion
import re
import os
import openai

import json
from apikey import apikey

os.environ['OPENAI_API_KEY'] = apikey

# Create your views here.

model_name = 'text-davinci-003'
temperature = 0.0
openai.api_key = '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'
# model = OpenAI(model_name=model_name, temperature=temperature, max_tokens=2000)


class Exercise(BaseModel):
    name: str
    body_parts: list[str]
    set: int
    rep: int


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
    date: date
    warmup: list[Exercise]
    workout: list[Exercise]
    cooldown: list[Exercise]


# llm = OpenAI(temperature = temperature)

# @csrf_protect
# @csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def getWorkout(request):
    input_data = request.POST

    user_email = Token.objects.get(key=request.auth).user

    # def convertData(data):
    #   result = []
    #    for execise in data:
    #         result.append(execise.dict())

    #     return result

    user = User.objects.get(email=user_email)

    userSerializer = UserFullSerializer(user)
    print(userSerializer.data)

    # messages = [{'role': 'user',
    #              'content': 'create a 30 minutes exercise for the lower back, with 5 minutes warmup, 20 minutes workout, and 5 minutes cooldown'}]

    # instance_of_my_data = pydantic_chatcompletion.create(
    #     messages, WorkoutFormat, model='gpt-3.5-turbo')

    # data = {'date': instance_of_my_data.date}
    # data['warmup'] = convertData(instance_of_my_data.warmup)
    # data['workout'] = convertData(instance_of_my_data.workout)
    # data['cooldown'] = convertData(instance_of_my_data.cooldown)

    # return JsonResponse(data, safe=False)

    return HttpResponse({'hello'})
