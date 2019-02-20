from datetime import datetime, timedelta
import random, string

from django.contrib import auth
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from workers import task

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
               'Access denied to current user']


def get_user_logged_in(request):
    return request.user.is_authenticated


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


def index(request):
    """
    The function that is returned after the use calls the index of the API path
    Path: 'api/'
    """
    return HttpResponse('API Home')


@csrf_exempt
def login(request):
    """
    The function that represents the API call to login a user.
    Path: 'api/login/'
    Request Type: POST

    Args:
        - request -- the HTTP request made to the url

    Required Request Parameters:
        - username -- the username of the user to login
        - password -- the password of the provided user

    Return:
        - JSON object -- a json object with either a completed or error status
    """

    if get_user_logged_in(request):
        return JsonResponse(get_error_object(3))

    try:
        username = request.POST['username']
        user = User.objects.get(username=username)
        is_correct_password = user.check_password(request.POST['password'])
        if not is_correct_password:
            return JsonResponse(get_error_object(5))
        auth.login(request, user)

    except KeyError:
        return JsonResponse(get_error_object(4))

    except User.DoesNotExist:
        return JsonResponse(get_error_object(2))

    return JsonResponse(get_success_object())


@csrf_exempt
def register(request):
    """
        The function that represents the API call to register a new user.
        Path: 'api/register/'
        Request Type: POST

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            username -- the username of the user to create
            password -- the password of the provided user
            email -- the email of the user

        Optional Request Parameters:
            first_name -- the first name of the user
            last_name -- the last name of the user

        Return:
            JSON object -- a json object with either a completed or error status
        """
    if get_user_logged_in(request):
        return JsonResponse(get_error_object(3))

    try:
        username = request.POST['username']
        password = request.POST['password']
        validate_password(password)
        email = request.POST['email']
        u = User.objects.create(username=username, email=email)
        u.set_password(password)

        if 'first_name' in request.POST:
            u.first_name = request.POST['first_name']

        if 'last_name' in request.POST:
            u.last_name = request.POST['last_name']

        u.save()
        s = Student.objects.create(user=u)
        s.save()

    except KeyError:
        return JsonResponse(get_error_object(4))

    except ValidationError:
        return JsonResponse(get_error_object(6))

    except IntegrityError:
        return JsonResponse(get_error_object(7))

    return JsonResponse(get_success_object())


def logout(request):
    """
        The function that represents the API call to logout a user.
        Path: 'api/logout/'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Return:
            JSON object -- a json object with either a completed or error status
        """
    if not get_user_logged_in(request):
        return JsonResponse(get_error_object(0))

    auth.logout(request)
    return JsonResponse(get_success_object(), content_type="application/json")


def request_password_reset(request, username):
    """
        The function that represents the API call to reset the password of a user.
        Path: 'api/request_password_reset/<str:username>'
        Request Type: GET

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            username -- the username of the user to reset the password for

        Return:
            JSON object -- a json object with either a completed or error status

        Additional Information:
            The user's email should receive a 6 digit reset code for resetting their password.
            The reset code will expire after one hour.
        """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse(get_error_object(2))

    student_account = Student.objects.get(user=user)

    if student_account.reset_password_code is not None:
        return JsonResponse(get_error_object(8))

    reset_code = generate_reset_code()
    student_account.reset_password_code = reset_code
    student_account.save()
    reset_code_timeout(str(student_account.id), _schedule=datetime.now() + timedelta(minutes=60))

    send_mail('ICBA - Reset Password Link',
              'Dear %s,\n\n\tYour password reset code is: %s\n\n\tThis link will only be active '
              'for 1 hour.\n\n\tIf you did not request this password reset, ignore this email\n\nThanks,\nICBA App' % (
                  user.first_name, str(reset_code)
              ),
              'icbadeveloper2019@gmail.com', [user.email])

    return JsonResponse(get_success_object())


def generate_reset_code():
    """
        The function that will generate a random string of uppercase letters and digits with a length of 6.

        Return:
            String -- a random string of 6 characters
    """
    reset_code = ''
    for i in range(6):
        reset_code += random.choice(string.ascii_uppercase + string.digits)
    return reset_code


@task()
def reset_code_timeout(student_id):
    """
        The function that is scheduled after 60 minutes to remove the student's reset code.
    """
    student_account = Student.objects.get(id=student_id)
    student_account.reset_password_code = None
    student_account.save()


def remove_reset_code(student_account):
    """
        The function that runs after a user puts in the correct reset code and resets their password.

        Args:
             student_account -- The student account associated with the reset code
    """
    student_account.reset_password_code = None
    student_account.save()


def reset_password(request, reset_code):
    """
        The function that represents the API call to login a user.
        Path: 'api/reset_password/<str:reset_code>'
        Request Type: POST

        Args:
            request -- the HTTP request made to the url

        Required Request Parameters:
            new_password -- the new password the user wants their password to be

        Return:
            JSON object -- a json object with either a completed or error status
    """
    try:
        student_account = Student.objects.get(reset_password_code=reset_code)
        request.user.set_password(request.POST['new_password'])
        remove_reset_code(student_account)

    except KeyError:
        return JsonResponse(get_error_object(1))

    except Student.DoesNotExist:
        return JsonResponse(get_error_object(2))

    return JsonResponse(get_success_object())


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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    if request.user.groups.filter(name="professor").exists():
        group = "professor"
    elif request.user.groups.filter(name="administrator").exists():
        group = "administrator"
    else:
        group = "student"

    success_object = get_success_object()
    success_object['object'] = {'group': group}
    return JsonResponse(success_object)


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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    if request.method != "POST":
        return JsonResponse(get_error_object(10))

    s = Student.objects.get(user=request.user)

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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    if request.method != "POST":
        return JsonResponse(get_error_object(10))

    s = Student.objects.get(user=request.user)

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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    s = Student.objects.get(user=request.user)

    try:
        demo_instance = Demographic.objects.get(student=s)
        demo_instance.delete()
        return JsonResponse(get_success_object())

    except Demographic.DoesNotExist:
        return JsonResponse(get_error_object(2))


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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    s = Student.objects.get(user=request.user)

    try:
        demo_instance = Demographic.objects.get(student=s)
        object_dict = demo_instance.to_dict()
        success_object = get_success_object()
        success_object['object'] = object_dict
        return JsonResponse(success_object)

    except Demographic.DoesNotExist:
        return JsonResponse(get_error_object(2))


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

    current_student = Student.objects.get(user=request.user)

    try:
        x = request.GET['x']
        y = request.GET['y']
        new_position = Position.objects.create(id=uuid.uuid4(), student=current_student, x=x, y=y)
        new_position.save()
        return JsonResponse(get_success_object())

    except KeyError:
        return JsonResponse(get_error_object(4))


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

    current_student = Student.objects.get(user=request.user)

    positions = []
    for pos in Position.objects.filter(student=current_student):
        positions.append({'id': pos.id, 'x': pos.x, 'y': pos.y, 'time': pos.timestamp})

    return JsonResponse({'positions': positions})


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

    current_student = Student.objects.get(user=request.user)

    try:
        pos = Position.objects.get(id=request.GET['id'])
        if pos.student != current_student:
            return JsonResponse(get_error_object(12))
        return JsonResponse({'position': {'id': pos.id, 'x': pos.x, 'y': pos.y, 'time': pos.timestamp}})

    except KeyError:
        return JsonResponse(get_error_object(4))


