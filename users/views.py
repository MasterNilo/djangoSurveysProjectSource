from django.urls import reverse_lazy
from django.views import generic

from users.forms import CustomUserCreationForm


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class SignedOutView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signed_out_url')
    template_name = 'registration/signed_out.html'