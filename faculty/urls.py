from django.urls import path
from faculty.views import *


urlpatterns = [
    path('', dashboard),

    path('class/overview', class_overview),
    path('class/create', class_create),
    path('class/<uuid:class_id>/view', class_view),
    path('class/<uuid:class_id>/remove_student/<uuid:student_id>', class_remove_student),
    path('class/<uuid:class_id>/add_student/<str:first_name>&<str:last_name>', class_add_student),
    path('class/<uuid:class_id>/edit', class_edit),
    path('class/save_form', class_save_form),
    path('class/<uuid:class_id>/remove', class_remove),
    path('class/<uuid:class_id>/remove_confirm', class_remove_confirm)
]