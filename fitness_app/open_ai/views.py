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
from typing import Optional
from dotenv import load_dotenv

import pydantic_chatcompletion

import re
import os
from openai import OpenAI
import openai

import json

load_dotenv()

# os.environ['OPENAI_API_KEY'] = apikey


api_key = os.environ.get('API_KEY')


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
    workoutLevel, workoutTime, workoutEquipment, muscleGroup, workoutGoal = request.data.items()
    user_email = Token.objects.get(key=request.auth).user

    def convertData(data):
        result = []
        for execise in data:
            result.append(execise.dict())
        return result

    user = User.objects.get(email=user_email)

    userSerializer = UserFullSerializer(user)
    goals = userSerializer.data['workoutGoals'][0]['goals']
    userData = userSerializer.data

    user_goals = []
    for goal in goals:
        user_goals.append(goal['goal'])

    user_equipments = []
    for equipment in userSerializer.data['EquipmentsList'][0]['equipments']:
        user_equipments.append(equipment['name'])

    user_preference = []
    for preference in userSerializer.data['workoutPreference'][0]['preference']:
        user_preference.append(preference['name'])

    messages = {'role': 'user',
                'content': f"""

                You are a spontaneous fitness trainer. \n
                Create a personalize {workoutTime[1]} {workoutLevel[1]} level workout for your client that is a {userData['gender']}, {userData['age']} years old, {userData['height']['feet']} feet and {userData['height']['inches']} inches tall and weights {userData['weight']} focusing on {muscleGroup[1]} muscle for {workoutGoal[1]} 

                output your response in JSON format below:

                workout: {{
                    warmup:[{{
                        name: string
                        body_parts: list[string]
                        set: number
                        rep: number or undefined
                        duration: number in seconds or undefined
                        rest_duration: number or undefined}}
                        ]
                    ,
                    workout: [{{
                        name: string
                        body_parts: list[string]
                        set: number
                        rep: number or undefined
                        duration: number in seconds or undefined
                        rest_duration: number or undefined}}
                        ],
                    cooldown: [{{
                        name: string
                        body_parts: list[string]
                        set: number
                        rep: number or undefined
                        duration: number in seconds or undefined
                        rest_duration: number or undefined}}
                        ]
                }}
            

                """
                }

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a professional fitness trainer design to help create fitness workouts. output result in JSON."},
            {**messages}
        ]
        )

    data = json.loads(response.choices[0].message.content)['workout']
    data['date'] = date.today()

    return JsonResponse(data, safe=False)
