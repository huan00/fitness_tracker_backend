from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class EmailAuthBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            user = get_user_model().objects.get(email=username)
            # user = User.objects.get(email=username) #switch to get_user_model()
            if user.checkpassword(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
