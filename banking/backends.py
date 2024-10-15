from datetime import datetime
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password, make_password
from .models import User

class CustomBackend(BaseBackend):
    def authenticate(self, request=None, username=None, password=None):
        try:
            user = User.objects.get(username=username)

            if check_password(password, user.password):
                user.last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user.save()
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    