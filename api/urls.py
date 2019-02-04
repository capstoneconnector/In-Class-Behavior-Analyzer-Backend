from django.urls import path

from .views import *

urlpatterns = [
    path('', index),
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
    path('reset_password/<str:reset_code>', reset_password),
    path('request_password_reset/<str:username>', request_password_reset),
    path('demographic/', demographic_form),
    path('position/', position_form)
]
