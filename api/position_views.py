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
        Function Summary: This function is used to create a Position object.
        Path: 'api/position/create'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user
            x -- The x position of the user
            y -- The y position of the user

        Possible Error Codes:
            300, 301, 302

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using a GET request.
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    # Ensure that the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    # Get the currently logged in Student object.
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Try to create a new Position object and return a success status.
    try:
        x = request.GET['x']
        y = request.GET['y']
        time = timezone.localtime(timezone.now())
        new_position = Position.objects.create(student=current_student, x=x, y=y, timestamp=time)
        new_position.save()

        success_status = Response.get_success_status()
        success_status['data'] = new_position.to_dict()
        return JsonResponse(success_status)

    except KeyError:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))


@csrf_exempt
def position_select_all(request):
    """
        Function Summary: This function is used to get all of the Positions objects for a Student.
        Path: 'api/position/all'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Possible Error Codes:
            300, 301

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using a GET request.
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    # Ensure the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    # Get the currently logged in Student object.
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Get all of the dictionary objects of the Position objects for the current Student.
    positions = [x.to_dict() for x in Position.objects.filter(student=current_student)]

    # Return the success status with the Position objects.
    success_status = Response.get_success_status()
    success_status['data'] = positions

    return JsonResponse(success_status)


@csrf_exempt
def position_select_id(request):
    """
        Function Summary: This function is used to get a single Position object's information.
        Path: 'api/position/select'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user
            position_id -- The Position ID to be looked up

        Possible Error Codes:
            300, 301, 302, 303, 304

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using a GET request.
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    # Ensure the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    # Get the currently logged in Student object.
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Ensure that the request's GET parameters include 'position_id'.
    if 'position_id' not in request.GET:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))

    # Lookup the Position using the provided 'position_id'.
    position_lookup = Position.objects.filter(id=request.GET['position_id'])

    # If no Position object exists, return an error status.
    if len(position_lookup) == 0:
        return JsonResponse(Response.get_error_status(303, POSITION_ERRORS))

    # Get the current Position.
    current_position = position_lookup[0]

    # If the logged in User is not the User listed in the Position, return an error status
    if current_position.student != current_student:
        return JsonResponse(Response.get_error_status(304, POSITION_ERRORS))

    # Return a success status with the Position data.
    success_status = Response.get_success_status()
    success_status['data'] = current_position.to_dict()
    return JsonResponse(success_status)


@csrf_exempt
def position_summary(request):
    """
        Function Summary: This function is used to get the Position history of a User.
        Path: 'api/position/summary'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user
            start_time -- The start time to search for
            end_time -- The end time to search for

        Possible Error Codes:
            300, 301, 302, 305, 306

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using a GET request.
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(301, POSITION_ERRORS))

    # Ensure the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(300, POSITION_ERRORS))

    # Get the currently logged in Student object.
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Ensure that 'start_time' and 'end_time' are in the GET parameters.
    if 'start_time' not in request.GET or 'end_time' not in request.GET:
        return JsonResponse(Response.get_error_status(302, POSITION_ERRORS))

    # Try to parse the start and end times into DateTime objects. Return error status if the string is invalid.
    try:
        start_datetime = parse_datetime(request.GET['start_time'])
        end_datetime = parse_datetime(request.GET['end_time'])

    except ValueError:
        return JsonResponse(Response.get_error_status(305, POSITION_ERRORS))

    if start_datetime is None or end_datetime is None:
        return JsonResponse(Response.get_error_status(306, POSITION_ERRORS))

    # Convert start and end times into local time
    start_datetime = timezone.localtime(timezone.make_aware(start_datetime))
    end_datetime = timezone.localtime(timezone.make_aware(end_datetime))

    # Return a success status with the position summary information.
    success_object = Response.get_success_status()
    success_object['data'] = [x.to_dict() for x in Position.objects.filter(student=current_student, timestamp__gt=start_datetime, timestamp__lt=end_datetime).order_by('timestamp')]

    return JsonResponse(success_object)
