from django.urls import path, include


from . import views
from .views import UserLoginView, UserRegisterView


urlpatterns = [
    path('login', UserLoginView.as_view(), name='api_login' ),
    path('register', UserRegisterView.as_view(), name='api_register')
]
