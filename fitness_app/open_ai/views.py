from django.shortcuts import render
from django.http import JsonResponse,  HttpResponse
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import Field, validator, BaseModel
from langchain.output_parsers import PydanticOutputParser
from typing import List
from datetime import datetime

import re
import os
from apikey import apikey

os.environ['OPENAI_API_KEY'] = apikey

# Create your views here.

model_name = 'text-davinci-003'
temperature = 0.0
model = OpenAI(model_name=model_name, temperature=temperature, max_tokens=1000)


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
    rest: int


class HIITWorkoutFormat(BaseModel):
    date: datetime
    number_set: int
    exercises: List[HIITExercise]


class WorkoutFormat(BaseModel):
    date: datetime
    warmup: List[Exercise]
    exercises: List[Exercise]
    cooldown: List[Exercise]


def generateWorkout():
    exercisePrompt = 'You are a highly renowned expert FitnessGPT. {format_instructions}. I am {age} years old, {gender}, {height}. My current weight is {weight}. My primary fitness and health goals are {goal}. This week I have worked out for {daysWorkedOut} days, where I worked on my {muscleGroup}. I want a {level} {workoutType} workout that focuses on {bodyArea} for {lengthOfTime} with {equipment}. Create a detailed workout with movements, rep amounts, and suggestion of added weight according to my preferences that helps me achieve my goals and {repetitionType}. Don\’t break character under any circumstance.'

    parser = PydanticOutputParser(pydantic_object=WorkoutFormat)

    prompt = PromptTemplate(
        template=exercisePrompt,
        input_variables=['age', 'gender', 'height', 'weight',
                         'goal', 'daysWorkedOut', 'muscleGroup', 'level', 'workoutType', 'bodyArea', 'lengthOfTime', 'equipment', 'repetitionType'],
        partial_variables={
            'format_instructions': parser.get_format_instructions()}
    )

    _input = prompt.format_prompt(age=31, gender='female', height='5.2 foot', weight='155lb',
                                  goal='weight loss', daysWorkedOut=2, muscleGroup='chest and arm', level='professional', workoutType='strenght training', bodyArea='abs', lengthOfTime='30 minutes',  equipment='gym equipments', repetitionType='avoid same workout for the week')

    output = model(_input.to_string())

    file = open('result.json', 'w')
    file.write(output)
    file.close()

    # print(output)

    result = parser.parse(output)
    json_object = result.json()
    return json_object


# llm = OpenAI(temperature = temperature)

def getWorkout(request):

    output = generateWorkout()

    # file = open('result.json', 'w')
    # file.write(output)
    # file.close()
    return HttpResponse(output)
