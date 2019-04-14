from .models import Student, Session
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.password_validation import validate_password, ValidationError

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
    110: 'No group associated with current user',
    111: 'Not strong enough password'
}


def get_user_logged_in(request):
    """
        Function Summary: This will get whether a user is logged in or not.

        Args:
            request -- The request object containing the 'session_id' in GET parameters

        Return:
            Type: boolean
            Data: If the 'session_id' is not in GET or the Session object does not exist, False will be returned. Otherwise, true will be returned
    """
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
    """
        Function Summary: This will get the user by the 'session_id' provided. This should be run after 'get_user_logged_in()' to ensure that no errors are thrown.

        Args:
            session_id -- The session_id to get the user by

        Return:
            Type: User
            Data: The User object that is connected to the 'session_id'
        """
    return Session.objects.get(id=session_id).user


def is_user_session_valid(session_id):
    """
        Function Summary: This will check whether a 'session_id' is valid or not.

        Args:
            session_id -- The Session ID to be checked for validity

        Return:
            Type: boolean
            Data: Will return False if the ID does not exist and True otherwise
    """
    return len(Session.objects.filter(id=session_id)) == 1


def generate_reset_code():
    """
        Function Summary: This function will generate a random six-digit reset code for use in the password reset function. The string will contain only uppercase letters and digits.

        Args:

        Return:
            Type: string
            Data: A random six-digit string
    """
    reset_code = ''
    for i in range(6):
        reset_code += random.choice(string.ascii_uppercase + string.digits)
    return reset_code


@task()
def expire_reset_code(student_id):
    """
        Function Summary: This function is a task that will remove the reset code on a Student object. This is used by the Django-Workers library to expire the reset code after an hour.

        Args:
            student_id -- The ID of the Student object

        Return:
            Type: None
    """
    student = Student.objects.get(id=student_id)
    student.reset_password_code = ''
    student.save()


@csrf_exempt
def login(request):
    """
        Function Summary: This function will login a user and return a session_id to use to authenticate into the API.
        Path: '/api/auth/login'
        Request Type: POST
        Required Login: False

        Args:
            request -- The request made to the server by the client

        Required POST parameters:
            username -- The username for the user
            password -- The password for the user

        Possible Error Codes:
            101, 103, 104, 105

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. If successful, it will have a data object containing the 'session_id' for authentication
    """
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
    """
        Function Summary: This function is used to create a new User and Student.
        Path: '/api/auth/register'
        Request Type: POST
        Required Login: False

        Args:
            request -- The request made to the server from the client

        Required POST parameters:
            username -- The username to be created
            password -- The password to be created. This will be hashed by the server
            email -- The email associated with the new account
            first_name -- The first name on the new account
            last_name -- The last name on the new account

        Possible Error Codes:
            101, 103, 106

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
    """
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

    # Validate that the password provided is strong enough
    try:
        validate_password(request.POST['password'])
    except ValidationError:
        return JsonResponse(Response.get_error_status(111, AUTH_ERRORS))

    # Create new user
    new_user = User.objects.create(username=request.POST['username'],
                                   email=request.POST['email'],
                                   first_name=request.POST['first_name'],
                                   last_name=request.POST['last_name'])

    new_user.set_password(request.POST['password'])
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
    """
        Function Summary: This function is used to logout a User and remove their session_id if it exists.
        Path: '/api/auth/logout'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server from the client

        Required GET parameters:
            session_id -- The Session ID of the User to be logged out

        Possible Error Codes:
            100, 101

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
    """
    # Make sure the request is using POST to pass data
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

    # Ensure that the 'session_id' exists in the GET parameters
    if 'session_id' not in request.GET:
        return JsonResponse(Response.get_error_status(100, AUTH_ERRORS))

    # Lookup Session objects using the 'session_id' provided
    session_lookup = Session.objects.filter(id=request.GET['session_id'])

    # Return error if there are no Session objects with the provided 'session_id'
    if len(session_lookup) == 0:
        return JsonResponse(Response.get_success_status())

    # Delete the Session object and return a success
    current_session = session_lookup[0]
    current_session.delete()
    return JsonResponse(Response.get_success_status())


@csrf_exempt
def request_password_reset(request, username):
    """
        Function Summary: This function is used to request a password reset for a User. The user will receive an email containing a reset code if successful. This is only to be used for resetting Student passwords. The reset code is only active for one hour.
        Path: '/api/auth/request_password_reset/<USERNAME>'
        Request Type: GET
        Required Login: False

        Args:
            request -- The request made to the server by the client
            username -- The username provided to request the password reset for

        Possible Error Codes:
            101, 104, 107

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
    """
    # Ensure the API call is using GET method
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

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
    """
        Function Summary: This function is used to reset a password. The function requires a new password in the POST parameters and the proper reset code to reset the password. The user will receive an email notification that their password has been changed.
        Path: '/api/auth/reset_password/<RESET CODE>'
        Request Type: POST
        Required Login: False

        Args:
            request -- The request made to the server by the client
            reset_code -- The reset code emailed to the user

        Required POST parameters:
            new_password -- The new password for the User

        Possible Error Codes:
            101, 103, 108

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
    """
    # Check that the request was made using POST
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(101, AUTH_ERRORS))

    # Check that the POST data contains new password
    if 'new_password' not in request.POST:
        return JsonResponse(Response.get_error_status(103, AUTH_ERRORS))

    # Check that the reset code is registered to a user
    student_lookup = Student.objects.filter(reset_password_code=reset_code)

    if len(student_lookup) == 0:
        return JsonResponse(Response.get_error_status(108, AUTH_ERRORS))

    student_account = student_lookup[0]

    # Change the user's password
    new_password = request.POST['new_password']
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
