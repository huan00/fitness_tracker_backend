from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer


# Create your views here.

from .models import User

class UserLoginView(ObtainAuthToken):
    def post (self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response ({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(email = email, password = password)

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
        # email = request.data.get('email')
        # password = request.data.get('password')

        # if email is None or password is None:
        #     return Response({'error': 'Please provide email, and password'}, status = status.HTTP_400_BAD_REQUEST)
        
        # user = User(email=email, password = make_password(password))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)