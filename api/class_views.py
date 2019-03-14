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

    if not current_user.groups.filter(name='Professors').exists() and not current_user.groups.filter(
            name='Administrators').exists():
        return JsonResponse(get_error_status(404))

    admin_user_lookup = User.objects.filter(username=request.POST['admin'])

    if len(admin_user_lookup) == 0:
        return JsonResponse(get_error_status(405))

    admin_user = admin_user_lookup[0]

    new_class = Class.objects.create(title=request.POST['title'], semester=request.POST['semester'],
                                     year=request.POST['year'], admin=admin_user)
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
def class_summarize_student_movement(request):
    if not get_user_logged_in(request):
        return JsonResponse(get_error_status(400))

    if request.method != "POST":
        return JsonResponse(get_error_status(401))

    current_user = get_user_by_session(request.GET['session_id'])

    if 'class' not in request.POST or 'start_date' not in request.POST or 'end_date' not in request.POST:
        return JsonResponse(get_error_status(403))

    class_lookup = Class.objects.filter(id=request.POST['class'])

    if len(class_lookup) == 0:
        return JsonResponse(get_error_status(407))

    current_class = class_lookup[0]
    start_date = datetime.datetime.strptime(request.POST['start_date'], '%m/%d/%Y').date()
    end_date = datetime.datetime.strptime(request.POST['end_date'], '%m/%d/%Y').date()
    days_of_the_week = [x.id for x in current_class.days_of_the_week.all()]

    summary = {}

    for n in range((end_date - start_date).days + 1):
        current_date = start_date + datetime.timedelta(days=n)
        if current_date.weekday() not in days_of_the_week:
            continue

        start_timestamp = datetime.datetime(year=current_date.year, month=current_date.month, day=current_date.day,
                                            hour=current_class.start_time.hour, minute=current_class.start_time.minute)

        end_timestamp = datetime.datetime(year=current_date.year, month=current_date.month, day=current_date.day,
                                          hour=current_class.end_time.hour, minute=current_class.end_time.minute)
        summary[str(current_date)] = {}
        for student in current_class.students.all():
            positions = Position.objects.filter(student=student, timestamp__gte=start_timestamp, timestamp__lte=end_timestamp)
            summary[str(current_date)][str(student.id)] = [p.to_dict() for p in positions]

    success_status = get_success_status()
    success_status['data'] = summary
    return JsonResponse(success_status)
