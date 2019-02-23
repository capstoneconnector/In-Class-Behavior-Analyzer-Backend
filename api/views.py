from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from .models import *

# Create your views here.

ERROR_TEXTS = ['No Logged in User',  # 0
               'No password provided',
               'Object does not exist',
               'Logged in used already',
               'Not enough information provided GET/POST',
               'Incorrect Password',  # 5
               'Not strong enough password',
               'Key exists in database already',
               'User already has a reset code',
               'Form could not validate with the given data',
               'Not using proper request method',  # 10
               'Object already exists',
               'Access denied to current user',
               'Invalid datetime object',
               'Invalid datetime format']


def get_user_logged_in(request):
    if 'session_id' in request.GET:
        session_id = request.GET['session_id']
    else:
        return False

    try:
        Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return False

    return True


def get_user_by_session(session_id):
    return Session.objects.get(id=session_id).user


def get_error_object(error_id):
    """
    Return the error object given a error id

    Keyword arguments:
        error_id -- the error id (index in the list)
    """
    if error_id <= len(ERROR_TEXTS):
        return {'status': {'error_id': error_id, 'error_text': ERROR_TEXTS[error_id]}}


def get_success_object():
    """
    Return the success object
    """
    return {'status': {'completed': 200}}


@csrf_exempt
def index(request):
    """
    The function that is returned after the use calls the index of the API path
    Path: 'api/'
    """
    return HttpResponse('API Home')


@csrf_exempt
def user_group(request):
    """
        This function is used to check the logged in users role.
        Path: api/user/group
        Request Type: GET

        Args:
            return -- the HTTP request made to the url

        Return:
            JSON object -- a json object with either a group object
    """
    is_user_logged_in = get_user_logged_in(request)

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    session_id = request.GET['session_id']

    current_user = get_user_by_session(session_id)

    if current_user.groups.filter(name="Professors").exists():
        group = "professor"
    elif current_user.groups.filter(name="Administrators").exists():
        group = "administrator"
    elif current_user.groups.filter(name="Students").exists():
        group = "student"
    else:
        return JsonResponse(get_error_object(0))

    success_object = get_success_object()
    success_object['data'] = {'group': group}
    return JsonResponse(success_object)


@csrf_exempt
def demographic_create(request):
    """
        This function is used to update or create a new demographic object.
        Path: 'api/demographic/create'
        Request Type: POST

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            age -- the age of the user
            gender -- the gender of the user
            grade_year -- the grade year of the user
            ethnicity -- the ethnicity of the user
            race -- the race of the user
            major -- the major of the user

        Return:
            JSON object -- a json object with either a completed or error status
    """
    is_user_logged_in = get_user_logged_in(request)

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    if request.method != "POST":
        return JsonResponse(get_error_object(10))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    if len(Demographic.objects.filter(student=s)) != 0:
        return JsonResponse(get_error_object(11))

    try:
        new_demographic = Demographic.objects.create(student=s,
                                                     age=request.POST['age'],
                                                     gender=GenderLookup.objects.get(id=request.POST['gender']),
                                                     grade_year=GradeYearLookup.objects.get(id=request.POST['grade_year']),
                                                     ethnicity=EthnicityLookup.objects.get(id=request.POST['ethnicity']),
                                                     race=RaceLookup.objects.get(id=request.POST['race']),
                                                     major=request.POST['major']
                                                     )
        new_demographic.save()
        return JsonResponse(get_success_object())

    except KeyError:
        return JsonResponse(get_error_object(4))

    except GenderLookup.DoesNotExist:
        return JsonResponse(get_error_object(2))

    except GradeYearLookup.DoesNotExist:
        return JsonResponse(get_error_object(2))

    except EthnicityLookup.DoesNotExist:
        return JsonResponse(get_error_object(2))

    except RaceLookup.DoesNotExist:
        return JsonResponse(get_error_object(2))


@csrf_exempt
def demographic_update(request):
    """
        This function is used to update or create a new demographic object.
        Path: 'api/demographic/update'
        Request Type: POST

        Args:
            request -- the HTTP request made to the url

        Optional Request Parameters:
            age -- the age of the user
            gender -- the gender of the user
            grade_year -- the grade year of the user
            ethnicity -- the ethnicity of the user
            race -- the race of the user
            major -- the major of the user

        Return:
            JSON object -- a json object with either a completed or error status
    """
    is_user_logged_in = get_user_logged_in(request)

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    if request.method != "POST":
        return JsonResponse(get_error_object(10))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        demo_instance = Demographic.objects.get(student=s)

    except Demographic.DoesNotExist:
        return JsonResponse(get_error_object(2))

    if 'age' in request.POST:
        demo_instance.age = request.POST['age']

    if 'gender' in request.POST:
        try:
            demo_instance.gender = GenderLookup.objects.get(id=request.POST['gender'])
        except GenderLookup.DoesNotExist:
            return JsonResponse(get_error_object(2))

    if 'grade_year' in request.POST:
        try:
            demo_instance.grade_year = GradeYearLookup.objects.get(id=request.POST['grade_year'])
        except GradeYearLookup.DoesNotExist:
            return JsonResponse(get_error_object(2))

    if 'ethnicity' in request.POST:
        try:
            demo_instance.ethnicity = EthnicityLookup.objects.get(id=request.POST['ethnicity'])
        except EthnicityLookup.DoesNotExist:
            return JsonResponse(get_error_object(2))

    if 'race' in request.POST:
        try:
            demo_instance.race = RaceLookup.objects.get(id=request.POST['race'])
        except RaceLookup.DoesNotExist:
            return JsonResponse(get_error_object(2))

    if 'major' in request.POST:
        demo_instance.major = request.POST['major']

    return JsonResponse(get_success_object())


@csrf_exempt
def demographic_delete(request):
    """
        This function is used to update or create a new demographic object.
        Path: 'api/demographic/delete'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Return:
            JSON object -- a json object with either a completed or error status
    """
    is_user_logged_in = get_user_logged_in(request)

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        demo_instance = Demographic.objects.get(student=s)
        demo_instance.delete()
        return JsonResponse(get_success_object())

    except Demographic.DoesNotExist:
        return JsonResponse(get_error_object(2))


@csrf_exempt
def demographic_select(request):
    """
        This function is used to update or create a new demographic object.
        Path: 'api/demographic/delete'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Return:
            JSON object -- a json object with either a completed or error status
    """
    is_user_logged_in = get_user_logged_in(request)

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        demo_instance = Demographic.objects.get(student=s)
        object_dict = demo_instance.to_dict()
        success_object = get_success_object()
        success_object['object'] = object_dict
        return JsonResponse(success_object)

    except Demographic.DoesNotExist:
        return JsonResponse(get_error_object(2))


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

    if not get_user_logged_in(request):
        return JsonResponse(get_error_object(0))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        x = request.GET['x']
        y = request.GET['y']
        time = timezone.localtime(timezone.now())
        new_position = Position.objects.create(id=uuid.uuid4(), student=current_student, x=x, y=y, timestamp=time)
        new_position.save()
        return JsonResponse(get_success_object())

    except KeyError:
        return JsonResponse(get_error_object(4))


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
    if not get_user_logged_in(request):
        return JsonResponse(get_error_object(0))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    positions = []
    for pos in Position.objects.filter(student=current_student):
        positions.append({'id': pos.id, 'x': pos.x, 'y': pos.y, 'time': pos.timestamp})

    return JsonResponse({'positions': positions})


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
    if not get_user_logged_in(request):
        return JsonResponse(get_error_object(0))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        pos = Position.objects.get(id=request.GET['id'])
        if pos.student != current_student:
            return JsonResponse(get_error_object(12))
        return JsonResponse({'position': {'id': pos.id, 'x': pos.x, 'y': pos.y, 'time': pos.timestamp}})

    except KeyError:
        return JsonResponse(get_error_object(4))


@csrf_exempt
def position_summary(request):
    if not get_user_logged_in(request):
        return JsonResponse(get_error_object(0))

    current_user = get_user_by_session(request.GET['session_id'])
    current_student = Student.objects.get(user=current_user)

    if request.method != "GET":
        return JsonResponse(get_error_object(10))

    if 'start' not in request.GET or 'end' not in request.GET:
        return JsonResponse(get_error_object(4))

    try:
        start_datetime = parse_datetime(request.GET['start'])
        end_datetime = parse_datetime(request.GET['end'])

    except ValueError:
        return JsonResponse(get_error_object(13))

    if start_datetime is None or end_datetime is None:
        return JsonResponse(get_error_object(14))

    start_datetime = timezone.localtime(timezone.make_aware(start_datetime))
    end_datetime = timezone.localtime(timezone.make_aware(end_datetime))

    positions = Position.objects.filter(student=current_student, timestamp__gt=start_datetime, timestamp__lt=end_datetime).order_by('timestamp')
    success_object = get_success_object()
    # noinspection PyTypeChecker
    success_object['data'] = [x.to_dict() for x in positions]

    return JsonResponse(success_object)



