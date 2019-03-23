from .models import Student, Session
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import random
import string
import datetime

from workers import task

from api.response_functions import Response

AUTH_ERRORS = {
    100: 'No session_id in parameters of url',
    101: 'Wrong request type',
    102: 'Not enough GET data',
    103: 'Not enough POST data',
    104: 'No user with that username',
    105: 'Wrong password for user',
    106: 'Username already exists in database',
    107: 'User already has a reset code',
    108: 'Bad reset code',
    109: 'No user logged in',
    110: 'No group associated with current user'
}


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


def is_user_session_valid(session_id):
    return len(Session.objects.filter(id=session_id)) == 1


def generate_reset_code():
    reset_code = ''
    for i in range(6):
        reset_code += random.choice(string.ascii_uppercase + string.digits)
    return reset_code


@task()
def expire_reset_code(student_id):
    student = Student.objects.get(id=student_id)
    student.reset_password_code = ''
    student.save()


@csrf_exempt
def login(request):
    # Make sure the request is using POST to pass data
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

    # Make sure that the POST data contains a username and password
    if 'username' not in request.POST or 'password' not in request.POST:
        return JsonResponse(Response.get_error_status(103, AUTH_ERRORS))

    # Lookup the user in the DB
    user_lookup = User.objects.filter(username=request.POST['username'])

    # Check that the user exists in the DB
    if len(user_lookup) == 0:
        return JsonResponse(Response.get_error_status(104, AUTH_ERRORS))

    # Check the password of the user
    user = user_lookup[0]
    is_password_correct = user.check_password(request.POST['password'])

    if not is_password_correct:
        return JsonResponse(Response.get_error_status(105, AUTH_ERRORS))

    # Check to see if the user already has a session token active
    session_lookup = Session.objects.filter(user=user)

    if len(session_lookup) == 0:
        current_session = Session.objects.create(user=user)
        current_session.save()
    else:
        current_session = session_lookup[0]

    success_dict = Response.get_success_status()
    success_dict['data'] = {'session_id': current_session.id}
    return JsonResponse(success_dict)


@csrf_exempt
def register(request):
    # Make sure the request is using POST to pass data
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

    # Make sure that the POST data contains a username, password, email, first name, and last name
    if 'username' not in request.POST or 'password' not in request.POST or 'email' not in request.POST \
            or 'first_name' not in request.POST or 'last_name' not in request.POST:
        return JsonResponse(Response.get_error_status(103, AUTH_ERRORS))

    # Make sure the username isn't already taken
    user_lookup = User.objects.filter(username=request.POST['username'])

    if len(user_lookup) is not 0:
        return JsonResponse(Response.get_error_status(106, AUTH_ERRORS))

    # Create new user
    new_user = User.objects.create(username=request.POST['username'],
                                   email=request.POST['email'],
                                   first_name=request.POST['first_name'],
                                   last_name=request.POST['last_name'])
    new_user.set_password(request.POST['password'])
    new_user.groups.add(Group.objects.get(name='Students'))
    new_user.save()

    # Create student object
    new_student = Student.objects.create(user=new_user)
    new_student.save()

    # Render the email template
    email_html = render_to_string('welcome_email.html',
                                  {'user': {'first_name': new_user.first_name, 'last_name': new_user.last_name}})
    text_content = strip_tags(email_html)

    # Send the email to the user's email
    email = EmailMultiAlternatives('Welcome to ICBA!', text_content, 'ICBA-NO-REPLY', [new_user.email])
    email.attach_alternative(email_html, 'text/html')
    email.send()

    return JsonResponse(Response.get_success_status())


@csrf_exempt
def logout(request):
    if 'session_id' not in request.GET:
        return JsonResponse(Response.get_error_status(100, AUTH_ERRORS))

    session_lookup = Session.objects.filter(id=request.GET['session_id'])

    if len(session_lookup) == 0:
        return JsonResponse(Response.get_success_status())

    current_session = session_lookup[0]
    current_session.delete()
    return JsonResponse(Response.get_success_status())


@csrf_exempt
def request_password_reset(request, username):
    # Lookup the user with the provided username
    user_lookup = User.objects.filter(username=username)

    if len(user_lookup) == 0:
        return JsonResponse(Response.get_error_status(104, AUTH_ERRORS))

    user_account = user_lookup[0]
    student_account = Student.objects.get(user=user_account)

    # Check if the student already has a reset code
    if student_account.reset_password_code is not None:
        return JsonResponse(Response.get_error_status(107, AUTH_ERRORS))

    # Generate a reset code
    reset_code = generate_reset_code()
    student_account.reset_password_code = reset_code
    student_account.save()

    # Schedule the removal of the reset code after 1 hour
    expire_reset_code(str(student_account.id), _schedule=timezone.now() + datetime.timedelta(hours=1))

    # Render the email template
    email_html = render_to_string('reset_code_email.html', {'user': {'first_name': user_account.first_name, 'last_name': user_account.last_name}, 'reset_code': reset_code})
    text_content = strip_tags(email_html)

    # Send the email to the user's email
    email = EmailMultiAlternatives('ICBA - Reset Code', text_content, 'ICBA-NO-REPLY', [user_account.email])
    email.attach_alternative(email_html, 'text/html')
    email.send()

    return JsonResponse(Response.get_success_status())


@csrf_exempt
def reset_password(request, reset_code):

    # Check that the reset code is registered to a user
    student_lookup = Student.objects.filter(reset_password_code=reset_code)

    if len(student_lookup) == 0:
        return JsonResponse(Response.get_error_status(108, AUTH_ERRORS))

    student_account = student_lookup[0]

    # Check that the reset code sent by the user is correct
    if student_account.reset_password_code != reset_code:
        return JsonResponse(Response.get_error_status(108, AUTH_ERRORS))

    # Check that the request was made using POST
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

    # Check that the POST data contains new password
    if 'new_password' not in request.POST:
        return JsonResponse(Response.get_error_status(103, AUTH_ERRORS))

    # Change the user's password
    new_password = request.POST
    student_account.reset_password_code = None
    student_account.user.set_password(new_password)
    student_account.user.save()
    student_account.save()

    # Send the user a notification email
    email_html = render_to_string('reset_password_notification_email.html',
                                  {'user': {'first_name': student_account.user.first_name, 'last_name': student_account.user.last_name}})
    text_content = strip_tags(email_html)

    email = EmailMultiAlternatives('ICBA - Password Changed', text_content, 'ICBA-NO-REPLY', [student_account.user.email])
    email.attach_alternative(email_html, 'text/html')
    email.send()

    return JsonResponse(Response.get_success_status())


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
        return JsonResponse(Response.get_error_status(109, AUTH_ERRORS))

    session_id = request.GET['session_id']

    current_user = get_user_by_session(session_id)

    if current_user.groups.filter(name="Professors").exists():
        group = "professor"
    elif current_user.groups.filter(name="Administrators").exists():
        group = "administrator"
    elif current_user.groups.filter(name="Students").exists():
        group = "student"
    else:
        return JsonResponse(Response.get_error_status(110, AUTH_ERRORS))

    success_object = Response.get_success_status()
    success_object['data'] = {'group': group}
    return JsonResponse(success_object)
