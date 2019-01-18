from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from threading import Timer
from .models import Student
from django.contrib import auth
import json, uuid

# Create your views here.

running_timers = {}


def index(request):
    return HttpResponse('API Home')


def login(request):
    return HttpResponse('Login Home')


def register(request):
    return HttpResponse('Register Home')


def logout(request):
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return HttpResponse(json.dumps({'status': {'error_id': 0, 'error_text': 'No Logged in User'}}))

    auth.logout(request)
    return HttpResponse(json.dumps({'status': {'completed': 200}}))


def request_password_reset(request, username):
    user = User.objects.get(username=username)
    student_account = Student.objects.get(user=user)
    reset_code = uuid.uuid4()
    student_account.reset_password_code = reset_code
    student_account.save()

    send_mail('ICBA - Reset Password Link',
              'Dear %s,\n\n\tYour password reset link is: %s/api/reset_password/%s\n\n\tThis link will only be active '
              'for 1 hour.\n\n\tIf you did not request this password reset, ignore this email\n\nThanks,\nICBA App' % (
                  request.user.first_name, request.META['HTTP_HOST'], str(reset_code)
              ),
              'icbadeveloper2019@gmail.com', [request.user.email])

    t = Timer(60*60, lambda: remove_reset_code(student_account))
    running_timers[student_account] = t
    t.start()

    return HttpResponse(json.dumps({'status': {'completed': 200}}))


def remove_reset_code(student_account):
    t = running_timers.pop(student_account)
    t.cancel()
    student_account.reset_password_code = None
    student_account.save()


def reset_password(request, reset_code):
    try:
        student_account = Student.objects.get(reset_password_code=reset_code)
        remove_reset_code(student_account)
        request.user.set_password(request.POST['new_password'])
    except KeyError:
        return HttpResponse(json.dumps({'status': {'error_id': 1, 'error_text': 'No password provided'}}))
    except Student.DoesNotExist:
        return HttpResponse(json.dumps({'status': {'error_id': 2, 'error_text': 'Object does not exist'}}))

    return HttpResponse(json.dumps({'status': {'completed': 200}}))


def add_demographics(request):
    return HttpResponse('Add Demographics Home')


def update_demographics(request):
    return HttpResponse('Update Demographics Home')


def add_position(request):
    return HttpResponse('Add Position Home')
