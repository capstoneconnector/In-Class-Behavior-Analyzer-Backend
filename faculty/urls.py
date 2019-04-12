from django.urls import path

from faculty.views import *

urlpatterns = [

    path('', dashboard),

    path('dashboard/', dashboard, name='dashboard'),
    path('positions_dashboard/', positions_dashboard, name='positions_dashboard'),
    path('survey_dashboard/', survey_dashboard, name='survey_dashboard'),
    path('feedback/', feedback, name='feedback'),
    path('register/', register, name='register'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('student_view_table/', student_view_table, name='student_view_table'),
    path('survey_questions/', survey_questions, name='survey_questions'),
    path('survey_responses/', survey_responses, name='survey_responses'),

    path('dashboard', class_overview),
    path('create', class_create),
    path('save_form', class_save_form),
    path('<int:class_id>/edit', class_edit),
    path('<int:class_id>/remove', class_remove),
    path('save_student_enrollment_form', enrollment_save_form),
    path('create', student_enrollment_create),
    path('<int:class_id>/view_student', class_view),
    path('<int:class_id>/add_student/<str:first_name>&<str:last_name>', add_students_specific_class),
    path('view_student_form', student_view_form),
    path('create', survey_question_create),
    path('save_survey_form', survey_save_form),
    path('view_question_form', question_form),
    path('save_question_form', question_save_form),
    path('view_responses', responses_view),
    path('view_questions', questions_view),
    path('<int:survey_id>/add_question', add_survey_question),
    path('<int:survey_id>/view_survey', survey_view)

]
