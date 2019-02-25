from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.auth_views import get_user_logged_in, get_user_by_session
from api.models import *


CLASS_ERRORS = {
    400: 'No logged in user',
    401: 'Wrong request type',
    402: 'Not enough GET data',
    403: 'Not enough POST data',
    404: 'User does not have permission to this',
    405: 'No user with that username',
    406: 'No student with that id',
    407: 'Class does not exist',
    408: 'Student already enrolled in Class'
}


def get_error_status(err_id):
    return {
        'status': 'error',
        'info': get_error_information(err_id)
    }


def get_error_information(err_id):
    return {
        'error_id': err_id,
        'error_text': CLASS_ERRORS[err_id]
    }


def get_success_status():
    return {
        'status': 'success'
    }


@csrf_exempt
def class_create(request):
    if not get_user_logged_in(request):
        return JsonResponse(get_error_status(400))

    if request.method != "POST":
        return JsonResponse(get_error_status(401))

    current_user = get_user_by_session(request.GET['session_id'])

    if 'title' not in request.POST or 'admin' not in request.POST or 'semester' not in request.POST or 'year' not in request.POST:
        return JsonResponse(get_error_status(403))

    if not current_user.groups.filter(name='Professors').exists() and not current_user.groups.filter(name='Administrators').exists():
        return JsonResponse(get_error_status(404))

    admin_user_lookup = User.objects.filter(username=request.POST['admin'])

    if len(admin_user_lookup) == 0:
        return JsonResponse(get_error_status(405))

    admin_user = admin_user_lookup[0]

    new_class = Class.objects.create(title=request.POST['title'], semester=request.POST['semester'], year=request.POST['year'], admin=admin_user)
    new_class.save()

    success_status = get_success_status()
    success_status['data'] = new_class.to_dict()
    return JsonResponse(success_status)


@csrf_exempt
def class_select_all(request):
    if not get_user_logged_in(request):
        return JsonResponse(get_error_status(400))

    current_user = get_user_by_session(request.GET['session_id'])

    success_status = get_success_status()
    class_lookup = Class.objects.filter(admin=current_user)
    success_status['data'] = [x.to_dict() for x in class_lookup]

    return JsonResponse(success_status)


@csrf_exempt
def class_enroll_student(request):
    if not get_user_logged_in(request):
        return JsonResponse(get_error_status(400))

    if request.method != "POST":
        return JsonResponse(get_error_status(401))

    current_user = get_user_by_session(request.GET['session_id'])

    if not current_user.groups.filter(name='Professors').exists() and not current_user.groups.filter(name='Administrators').exists():
        return JsonResponse(get_error_status(404))

    if 'student' not in request.POST or 'class' not in request.POST:
        return JsonResponse(get_error_status(403))

    student_lookup = Student.objects.filter(id=request.POST['student'])
    if len(student_lookup) == 0:
        return JsonResponse(get_error_status(406))

    current_student = student_lookup[0]

    class_lookup = Class.objects.filter(id=request.POST['class'])
    if len(class_lookup) == 0:
        return JsonResponse(get_error_status(407))

    current_class = class_lookup[0]

    enrollment_lookup = ClassEnrollment.objects.filter(class_enrolled=current_class, student=current_student)
    if len(enrollment_lookup) != 0:
        return JsonResponse(get_error_status(408))

    class_enrollment = ClassEnrollment.objects.create(class_enrolled=current_class, student=current_student)
    class_enrollment.save()

    success_status = get_success_status()
    success_status['data'] = class_enrollment.to_dict()

    return JsonResponse(success_status)
