from django.urls import path, include


from . import views
from .views import UserLoginView, UserRegisterView, add_program


urlpatterns = [
    path('login', UserLoginView.as_view(), name='api_login'),
    path('register', UserRegisterView.as_view(), name='api_register'),
    path('verifylogin', views.verifyLogin, name='verifyLogin'),
    path('program', add_program, name='add_program')
]
