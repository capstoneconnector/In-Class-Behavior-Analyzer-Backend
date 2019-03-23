from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from api.auth_views import get_user_logged_in, get_user_by_session
from api.models import *

from api.response_functions import Response

POSITION_ERRORS = {
    300: 'No logged in user',
    301: 'Wrong request method',
    302: 'Not enough GET data',
    303: 'Position does not exist',
    304: 'Invalid Student associated with Position',
    305: 'Invalid datetime object',
    306: 'Invalid datetime format'
}


@csrf_exempt
def position_create(request):
    """
        This function is used to update or create a new demographic object.
        Path: 'api/position/create'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            x -- the x position of the user
            y -- the y position of the user

        Return:
            JSON object -- a json object with either a completed or error status
    """
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        x = request.GET['x']
        y = request.GET['y']
        time = timezone.localtime(timezone.now())
        new_position = Position.objects.create(id=uuid.uuid4(), student=current_student, x=x, y=y, timestamp=time)
        new_position.save()

        success_status = Response.get_success_status()
        success_status['data'] = new_position.to_dict()
        return JsonResponse(success_status)

    except KeyError:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))


@csrf_exempt
def position_select_all(request):
    """
        This function is used to get all of the positions for the logged in user.
        Path: 'api/position/select/all'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Return:
            JSON object -- a json object with either a completed or error status
    """
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    positions = []
    for pos in Position.objects.filter(student=current_student):
        positions.append(pos.to_dict())

    success_status = Response.get_success_status()
    success_status['data'] = positions

    return JsonResponse(Response.get_success_status())


@csrf_exempt
def position_select_id(request):
    """
        This function is used to get an individual position using the id.
        Path: 'api/position/select'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            id -- the id of the position object

        Return:
            JSON object -- a json object with either a completed or error status
    """
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        pos = Position.objects.get(id=request.GET['id'])
        if pos.student != current_student:
            return JsonResponse(Response.get_error_status(304, POSITION_ERRORS))
        return JsonResponse({'position': {'id': pos.id, 'x': pos.x, 'y': pos.y, 'time': pos.timestamp}})

    except KeyError:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))


@csrf_exempt
def position_summary(request):
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    current_user = get_user_by_session(request.GET['session_id'])
    current_student = Student.objects.get(user=current_user)

    if 'start' not in request.GET or 'end' not in request.GET:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))

    try:
        start_datetime = parse_datetime(request.GET['start'])
        end_datetime = parse_datetime(request.GET['end'])

    except ValueError:
        return JsonResponse(Response.get_error_status(305, POSITION_ERRORS))

    if start_datetime is None or end_datetime is None:
        return JsonResponse(Response.get_error_status(306, POSITION_ERRORS))

    start_datetime = timezone.localtime(timezone.make_aware(start_datetime))
    end_datetime = timezone.localtime(timezone.make_aware(end_datetime))

    positions = Position.objects.filter(student=current_student, timestamp__gt=start_datetime, timestamp__lt=end_datetime).order_by('timestamp')
    success_object = Response.get_success_status()
    success_object['data'] = [x.to_dict() for x in positions]

    return JsonResponse(success_object)
