from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth.models import BaseUserManager
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer, ProgramSerializer, UserFullSerializer, GoalSerializer, EquipmentSerializer, WorkoutPreferenceSerializer, WorkoutGoalSerializer, EquipmentListSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes
from django.core.exceptions import ObjectDoesNotExist



# Create your views here.

from .models import User, WorkoutPreference, Program, EquipmentList, Equipment, Goal, WorkoutGoal


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):

        email = BaseUserManager.normalize_email(request.data.get('email')).lower()
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)

        userExist = User.objects.get(email=email)
        userDataSerializer = UserFullSerializer(userExist)

        userData = {'token': token.key, 'user': userDataSerializer.data}

        return Response(userData, status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # permission types IsAuthenticated, IsAdminUser, AllowAny, ISAuthenticatedOrReadOnly
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        data = request.data
        userData = {}
        for key in data:
            if key != 'workout_program' and key != 'equipment_list' and key != 'workout_goal':
                if key == 'height':
                    height_data = json.loads(data[key])
                    userData[key] = {'feet':height_data['feet'], 'inches': height_data['inches']}
                else:
                    userData[key] = data[key]

        workout_program = data['workout_program'].split(',')
        equipment_list = data['equipment_list'].split(',')
        workout_goal = data['workout_goal'].split(',')

        email = BaseUserManager.normalize_email(request.data.get('email'))
        # print(email)
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Please provide email, and password'}, status=status.HTTP_400_BAD_REQUEST)
        userData['email'] = email
        # user = User(email=email, password=make_password(password))
        serializer = self.get_serializer(data=userData)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # print(serializer.data['email'])

        user = User.objects.get(email=serializer.data['email'])
        user = UserSerializer(user)
        user = User.objects.get(id=user.data['id'])
        # print(user)

        # check if program exist if not create program and add it to user
        programList = Program.userProgram(workout_program)
        programListSerializer = ProgramSerializer(programList, many=True)

        WorkoutPreference.create(
            programs=programListSerializer.data, user=user)

        equipmentList = Equipment.userEquipment(equipment_list)
        equipmentListSerializer = EquipmentSerializer(equipmentList, many=True)

        EquipmentList.create(
            equipmentList=equipmentListSerializer.data, user=user)

        goalList = Goal.userGoal(workout_goal)
        goalListSerializer = GoalSerializer(goalList, many=True)

        WorkoutGoal.create(goalList=goalListSerializer.data, user=user)

        userReturnSerializer = UserFullSerializer(user)

        return Response(userReturnSerializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def verifyLogin(request):
    email = Token.objects.get(key=request.auth).user

    user = User.objects.get(email=email)

    if user is not None:
        userSerializer = UserFullSerializer(user)
        json_data = json.dumps(userSerializer.data)
        return Response(json_data, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def updateUser(request):
    email = Token.objects.get(key=request.auth).user
    updated_data = request.data

    user = User.objects.get(email=Token.objects.get(key=request.auth).user)
    # update user info
    if user is not None:
        User.objects.filter(email=user).update(**updated_data)
        return Response(status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def updateUserPref(request):
    user = User.objects.get(email=Token.objects.get(key=request.auth).user)
    userSerializer = UserFullSerializer(user)
    user_prefs = userSerializer.data['workoutPreference']
    # get user instance
    try:
        userWorkoutPref = WorkoutPreference.objects.get(user=userSerializer.data['id'])
        user_workoutPref = WorkoutPreferenceSerializer(userWorkoutPref)

        for idx, program in enumerate(user_workoutPref.data['preference']):
            if program['name'] not in request.data:
                remove_program = Program.objects.get(name=program['name'])
                userWorkoutPref.preference.remove(remove_program)
        # remove program if not in list
        for idx,program in enumerate(request.data ):
            if program not in json.dumps(user_workoutPref.data['preference']):
                new_program = Program.objects.get(name=program)
                userWorkoutPref.preference.add(new_program)
                userWorkoutPref.save()
        return Response(json.dumps(user_workoutPref.data), status=status.HTTP_202_ACCEPTED)
    # create new programlist
    except ObjectDoesNotExist:
        new_workoutPref = WorkoutPreference.objects.create(user=user)
        for idx,program in enumerate(request.data ):
            new_program = Program.objects.get(name=program)
            userWorkoutPref.preference.add(new_program)
        userWorkoutPref.save()
        
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Problem updating, try again later'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def updateUserWorkoutGoal(request):
    user = User.objects.get(email=Token.objects.get(key=request.auth).user)
    userSerializer = UserFullSerializer(user)
    
    try:
        # get user instance
        userWorkoutGoal = WorkoutGoal.objects.get(user=userSerializer.data['id'])
        user_workoutGoal = WorkoutGoalSerializer(userWorkoutGoal)

        for goal in user_workoutGoal.data['goals']:
            if goal['goal'] not in request.data:
                remove_goal = Goal.objects.get(goal=goal['goal'])
                userWorkoutGoal.goals.remove(remove_goal)
        # remove goal if not in list
        for idx, goal in enumerate(request.data):
            new_goal = Goal.objects.get(goal=goal)
            userWorkoutGoal.goals.add(new_goal)
        userWorkoutGoal.save()
        return Response(json.dumps(user_workoutGoal.data), status=status.HTTP_202_ACCEPTED)
    # create new goalist
    except ObjectDoesNotExist:
        new_workoutGoal = WorkoutGoal.objects.create(user=user)
        for idx,goal in enumerate(request.data ):
            new_goal = Goal.objects.get(goal=goal)
            userWorkoutGoal.goals.add(new_goal)
        userWorkoutGoal.save()
        
        return Response(status=status.HTTP_201_CREATED)
    else:

        return Response({'error': 'Problem updating, try again later'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def updateUserEquipment(request):
    user = User.objects.get(email=Token.objects.get(key=request.auth).user)
    userSerializer = UserFullSerializer(user)
    
    try:
        # get user instance
        userEquipment = EquipmentList.objects.get(user=userSerializer.data['id'])
        user_equipmentList = EquipmentListSerializer(userEquipment)

        # remove equipment if not in list
        for equipment in user_equipmentList.data['equipments']:
            if equipment['name'] not in request.data:
                remove_equipment = Equipment.objects.get(name=equipment['name'])
                userEquipment.equipments.remove(remove_equipment)
        #add requipment
        for idx, equipment in enumerate(request.data):
            new_equipment = Equipment.objects.get(name=equipment)
            userEquipment.equipments.add(new_equipment)
        userEquipment.save()
        return Response(json.dumps(user_equipmentList.data), status=status.HTTP_202_ACCEPTED)

    # create new equipmentlist
    except ObjectDoesNotExist:
        new_workoutGoal = WorkoutGoal.objects.create(user=user)
        for idx,equipment in enumerate(request.data ):
            new_equipment = Equipment.objects.get(name=equipment)
            userEquipment.equipments.add(new_equipment)
        userEquipment.save()
        
        return Response(status=status.HTTP_201_CREATED)
    else:

        return Response({'error': 'Problem updating, try again later'}, status=status.HTTP_400_BAD_REQUEST)
        
