from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        # Will get the user model specified by the AUTH_USER_MODEL from the file
        # settings.py.
        
        fields = ('email', 'username',)
        # Password fields are included by default. We only specify what we need.


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        # Will get the user model specified by the AUTH_USER_MODEL from the file
        # settings.py.
        
        fields = ('email', 'username',)
        # Password fields are included by default. We only specify what we need.