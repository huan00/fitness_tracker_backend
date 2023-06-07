from django.shortcuts import render
import json
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer, WorkoutPreferenceSerializer


# Create your views here.

from .models import User, WorkoutPreference


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = str.lower(request.data.get('email'))
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


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

        # workout_program = data['workout_program']
        equipment_list = data['equipment_list']
        workout_goal = data['workout_goal']

        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Please provide email, and password'}, status=status.HTTP_400_BAD_REQUEST)

        # user = User(email=email, password=make_password(password))
        serializer = self.get_serializer(data=userData)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # user = User.objects.get(id=serializer.data.id)

        # workout_program = WorkoutPreference.objects.get(
        #     name=data['workout_program'])
        # if workout_program:
        #     user.workout_preference = workout_program
        #     user.save()
        # else:
        #     workout_preference = WorkoutPreference()
        #     workout_preference.

        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


data = {'first_name': 'Huan', 'last_name': 'Zeng', 'email': 'Huan123@gmail.com', 'password': 'abc', 'age': '36', 'gender': 'male', 'weight': '200', 'height': '', 'profile_image': 'file:///Users/huanzeng/Library/Developer/CoreSimulator/Devices/5FB59EDA-E353-4B52-A3A7-79022E0C34D9/data/Containers/Data/Application/DFDC02FA-2E00-4A2B-82DB-84C6A886943D/Library/Caches/ExponentExperienceData/%2540huan00%252Ffitness_app/Camera/6D25E6CE-96A3-49FA-A6D1-9C6E1F7AEE18.jpg',
        'workout_program': 'Aerobic,Flexibility Training,Interval Training,Balance Training,CrossFit', 'equipment_list': 'Barbells,weight bench,resistance bands,kettlebells', 'workout_goal': 'Lost weight or body fat,Build muscle,Improve health'}
