from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from . import views
from .views import UserLoginView, UserRegisterView


urlpatterns = [
    path('login', UserLoginView.as_view(), name='api_login'),
    path('register', UserRegisterView.as_view(), name='api_register'),
    path('verifylogin', views.verifyLogin, name='verifyLogin'),
    path('updateuserpref', views.updateUserPref, name='updateUserPref'),
    path('updateuserworkoutgoal', views.updateUserWorkoutGoal, name='updateUserWorkoutGoal'),
    path('updateuserequipment', views.updateUserEquipment, name='updateUserEquipment'),
    path('updateuser', views.updateUser, name='updateUser'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
