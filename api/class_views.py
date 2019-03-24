from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.auth_views import get_user_logged_in, get_user_by_session
from api.models import *

from api.response_functions import Response

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


@csrf_exempt
def class_select_all(request):
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(400, CLASS_ERRORS))

    current_user = get_user_by_session(request.GET['session_id'])
    current_student = Student.objects.get(user=current_user)

    success_status = Response.get_success_status()
    class_lookup = [x.class_enrolled for x in ClassEnrollment.objects.filter(student=current_student)]
    success_status['data'] = [x.to_dict() for x in class_lookup]

    return JsonResponse(success_status)


@csrf_exempt
def class_summarize_movement(request):
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(400, CLASS_ERRORS))

    if request.method != "POST":
        return JsonResponse(Response.get_error_status(401, CLASS_ERRORS))

    if 'class' not in request.POST or 'start_date' not in request.POST or 'end_date' not in request.POST:
        return JsonResponse(Response.get_error_status(403, CLASS_ERRORS))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))
    class_lookup = Class.objects.filter(id=request.POST['class'])

    if len(class_lookup) == 0:
        return JsonResponse(Response.get_error_status(407, CLASS_ERRORS))

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

        positions = Position.objects.filter(student=current_student, timestamp__gte=start_timestamp, timestamp__lte=end_timestamp)
        summary[str(current_date)] = [p.to_dict() for p in positions]

    success_status = Response.get_success_status()
    success_status['data'] = summary
    return JsonResponse(success_status)

