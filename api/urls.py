from django.urls import path

from .views import *
from .auth_views import *
from .demographic_views import *
from .position_views import *
from .class_views import *
from .survey_views import *
from .feedback_views import *

urlpatterns = [
    path('', index),

    # Authentication
    path('auth/login', login),
    path('auth/register', register),
    path('auth/logout', logout),
    path('auth/reset_password/<str:reset_code>', reset_password),
    path('auth/request_password_reset/<str:username>', request_password_reset),

    # Demographic Requests
    path('demographic/create', demographic_create),
    path('demographic/update', demographic_update),
    path('demographic/delete', demographic_delete),
    path('demographic/select', demographic_select),
    path('demographic/form', demographic_form),

    # Position Requests
    path('position/create', position_create),
    path('position/select/all', position_select_all),
    path('position/select', position_select_id),
    path('position/summary', position_summary),

    # Class Requests
    path('class/select/all', class_select_all),
    path('class/movement_summary', class_summarize_movement),

    # Survey Requests
    path('survey/respond', add_responses_to_survey),
    path('survey/generate', end_session_create_survey_instance),
    path('survey/open_surveys', get_all_open_survey_instances),
    path('survey/get', get_survey_by_id),

    # Feedback Requests
    path('feedback/submit', feedback_create)
]
