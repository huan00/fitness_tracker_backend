from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils.email import normalize_email
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer, ProgramSerializer, UserFullSerializer, GoalSerializer, EquipmentSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes


# Create your views here.

from .models import User, WorkoutPreference, Program, EquipmentList, Equipment, Goal, WorkoutGoal


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        print('hit login')
        email = normalize_email(request.data.get('email'))
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
                    userData[key] = json.loads(data[key])
                else:
                    userData[key] = data[key]

        workout_program = data['workout_program'].split(',')
        equipment_list = data['equipment_list'].split(',')
        workout_goal = data['workout_goal'].split(',')

        email = normalize_email(request.data.get('email'))
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Please provide email, and password'}, status=status.HTTP_400_BAD_REQUEST)

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
    print(request.auth)
    email = Token.objects.get(key=request.auth).user

    user = User.objects.get(email=email)

    if user is not None:
        userSerializer = UserFullSerializer(user)
        json_data = json.dumps(userSerializer.data)
        return Response(json_data, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
# @api_view(['POST'])
def add_program(request, format=None):

    program = Program.create('build muscle')
    print(program)
    programSz = ProgramSerializer(program)
    print(programSz.data)

    return Response('hello')
