from django.urls import path

from .views import *
from .views import line_webhook

urlpatterns = [
    path('', home, name='home-page'),
    path('home2', home2, name='home2'),
    path('about/', aboutUs, name='about-page'),  # New URL pattern for aboutUs view
    path('contact/', contact, name='contact-page'),  # New URL pattern for contact view
    path("line/webhook/", line_webhook, name="line-webhook"),
    path('showcontact/', showContact, name='showcontact-page'),  # New URL pattern for contact view
    path('register/', userRegist, name='register-page'),  # New URL pattern for userRegist view
    path('profile/', userProfile, name='profile-page'),  # New URL pattern for userProfile view
    path('editprofile/', editProfile, name='editprofile-page'),  # New URL pattern for editProfile view
    path('action/<int:cid>/', actionPage, name='action-page'),  # New URL pattern for actionPage view
]