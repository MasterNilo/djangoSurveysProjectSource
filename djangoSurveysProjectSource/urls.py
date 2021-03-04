"""djangoSurveysProjectSource URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path

from surveys.views import AboutView
from surveys.views import HomepageView

urlpatterns = [
    path('admin/', admin.site.urls), # This is bad for production because easy to guess.
    # path('different-admin-page/', admin.site.urls), # It's better to have a different
                                                    # site for the admin page.
    
    path('accounts/', include('django.contrib.auth.urls')),
    # This is for the urls that take care of django's account urls
    
    path('accounts/', include('users.urls')),
    # This will take care of the CustomUser accounts related stuff. On this project,
    # only sign up, sign in, and sign out are implemented.
    
    path('', HomepageView.as_view(), name='home_url'),
    path('about/', AboutView.as_view(), name='about_url'),
    
    path('surveys/', include('surveys.urls')),
]
