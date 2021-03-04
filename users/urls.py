from django.urls import path

from users.views import SignUpView
from users.views import SignedOutView

urlpatterns = [
        path('signup/', SignUpView.as_view(), name='signup'),
        path('signed-out/', SignedOutView.as_view(), name='signed_out_url'),
]
