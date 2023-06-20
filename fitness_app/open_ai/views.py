from django.shortcuts import render
from django.http import JsonResponse,  HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.decorators import login_required
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import Field, validator, BaseModel
from langchain.output_parsers import PydanticOutputParser
from typing import List
from datetime import datetime
from user.models import User
from user.serializers import UserFullSerializer

import re
import os
import json
from apikey import apikey

os.environ['OPENAI_API_KEY'] = apikey

# Create your views here.

model_name = 'text-davinci-003'
temperature = 0.0
model = OpenAI(model_name=model_name, temperature=temperature, max_tokens=2000)


class Exercise(BaseModel):
    name: str
    body_parts: List[str]
    set: int
    rep: int


class HIITExercise(BaseModel):
    name: str
    body_parts: List[str]
    exercise_type: str
    duration: int
    rest_time: int


class HIITWorkoutFormat(BaseModel):
    date: datetime
    number_set: int
    exercises: List[HIITExercise]


class WorkoutFormat(BaseModel):
    date: datetime
    warmup: List[Exercise]
    exercises: List[Exercise]
    cooldown: List[Exercise]


def generateWorkout(user, input):
    # exercisePrompt = 'You are a highly renowned expert FitnessGPT. {format_instructions}. I am {age} years old, {gender}, {height}. My current weight is {weight}. My primary fitness and health goals are {goal}. This week I have worked out for {daysWorkedOut} days, where I worked on my {muscleGroup}. I want a {level} {workoutType} workout that focuses on {bodyArea} for {lengthOfTime} with {equipment}. Create a detailed workout with movements, rep amounts, and suggestion of added weight according to my preferences that helps me achieve my goals and {repetitionType}. Don\’t break character under any circumstance.'

    # print(json.load(user['height']))

    # exercisePrompt = 'You are a highly renowned expert FitnessGPT. {format_instructions}. I am {age} years old, {gender}, {height}. My current weight is {weight}. My primary fitness and health goals are {goal}. This week I have worked out for {daysWorkedOut} days, where I worked on my {muscleGroup}. I want a {level} {workoutType} workout for {lengthOfTime} with {equipment}. Create a detailed workout with movements, rep amounts, and suggestion of added weight according to my preferences that helps me achieve my goals. Don\’t break character under any circumstance.'
    exercisePrompt = 'You are a highly renowned expert FitnessGPT.\n {format_instructions}.\n I am {age} years old, {gender}, {height}. My current weight is {weight}. My primary fitness and health goals are {goal}. This week I have worked out for {daysWorkedOut} days. create a {level} {workoutType} of the day with reasonable number of sets, focusing on {muscleGroup} for {lengthOfTime} minutes with {equipment} each exercise should have a reasonable rest time'

    parser = PydanticOutputParser(pydantic_object=HIITWorkoutFormat)
    # parser = PydanticOutputParser(pydantic_object=WorkoutFormat)

    prompt = PromptTemplate(
        input_variables=['age', 'gender', 'height', 'weight',
                         'goal', 'daysWorkedOut', 'muscleGroup', 'level', 'workoutType', 'lengthOfTime', 'equipment'],
        template=exercisePrompt,
        partial_variables={
            'format_instructions': parser.get_format_instructions()}
    )

    inputEquipment = input['workoutEquipment'] == 'my equipments' if user['EquipmentsList'] else input['workoutEquipment']

    _input = prompt.format_prompt(age=user['age'], gender=user['gender'], height=user['height'], weight=user['weight'],
                                  # repetitionType='avoid same workout for the week'
                                  goal=user['workoutGoals'], daysWorkedOut=5, muscleGroup=input['muscleGroup'], level=input['workoutLevel'], workoutType='HIIT workout', lengthOfTime=int(input['workoutTime']),  equipment=inputEquipment,
                                  )

    output = model(_input.to_string())

    result = parser.parse(output)
    json_object = result.json()
    return json_object


# llm = OpenAI(temperature = temperature)

# @csrf_protect
# @csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def getWorkout(request):
    input_data = request.POST

    user = User.objects.get(email='return99@gmail.com')

    userSerializer = UserFullSerializer(user)

    output = generateWorkout(userSerializer.data, input_data)
    # output = ''

    return HttpResponse(output)
