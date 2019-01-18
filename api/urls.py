from django.urls import path

from .views import *

urlpatterns = [
    path('', index),
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
    path('reset_password/<uuid:reset_code>', reset_password),
    path('request_password_reset/<str:username>', request_password_reset),
    path('add_demographics/', add_demographics),
    path('update_demographics/', update_demographics),
    path('add_position/', add_position)
]
