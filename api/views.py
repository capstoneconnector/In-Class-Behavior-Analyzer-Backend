from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.core.mail import send_mail
from threading import Timer
from .models import *
from django.contrib import auth
import uuid

# Create your views here.

running_timers = {}
ERROR_TEXTS = ['No Logged in User', 'No password provided', 'Object does not exist', 'Logged in used already',
               'Not enough information provided GET/POST', 'Incorrect Password', 'Not strong enough password',
               'Key exists in database already']


def get_error_object(error_id):
    if error_id <= len(ERROR_TEXTS):
        return {'status': {'error_id': error_id, 'error_text': ERROR_TEXTS[error_id]}}


def get_success_object():
    return {'status': {'completed': 200}}


def index(request):
    return HttpResponse('API Home')


@csrf_exempt
def login(request):
    is_user_logged_in = request.user.is_authenticated

    if is_user_logged_in:
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

    return JsonResponse(get_success_object())


@csrf_exempt
def register(request):
    is_user_logged_in = request.user.is_authenticated

    if is_user_logged_in:
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
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0), content_type="application/json")

    auth.logout(request)
    return JsonResponse(get_success_object(), content_type="application/json")


def request_password_reset(request, username):
    user = User.objects.get(username=username)
    student_account = Student.objects.get(user=user)
    reset_code = uuid.uuid4()
    student_account.reset_password_code = reset_code
    student_account.save()

    send_mail('ICBA - Reset Password Link',
              'Dear %s,\n\n\tYour password reset link is: %s/api/reset_password/%s\n\n\tThis link will only be active '
              'for 1 hour.\n\n\tIf you did not request this password reset, ignore this email\n\nThanks,\nICBA App' % (
                  user.first_name, request.META['HTTP_HOST'], str(reset_code)
              ),
              'icbadeveloper2019@gmail.com', [user.email])

    t = Timer(60 * 60, lambda: remove_reset_code(student_account))
    running_timers[student_account] = t
    t.start()

    return JsonResponse(get_success_object(), content_type="application/json")


def remove_reset_code(student_account):
    t = running_timers.pop(student_account)
    t.cancel()
    student_account.reset_password_code = None
    student_account.save()


def reset_password(request, reset_code):
    try:
        student_account = Student.objects.get(reset_password_code=reset_code)
        request.user.set_password(request.POST['new_password'])
        remove_reset_code(student_account)

    except KeyError:
        return JsonResponse(get_error_object(1), content_type="application/json")

    except Student.DoesNotExist:
        return JsonResponse(get_error_object(2))

    return JsonResponse(get_success_object(), content_type="application/json")


def add_demographics(request):
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    try:
        s = Student.objects.get(user=request.user)
        age = request.POST['age']
        gender = request.POST['gender']
        grade_year = request.POST['grade_year']
        ethnicity = request.POST['ethnicity']
        race = request.POST['race']
        d = Demographic.objects.create(id=s,
                                       age=age,
                                       gender=GenderLookup.objects.get(id=int(gender)),
                                       grade_year=GradeYearLookup.objects.get(id=int(grade_year)),
                                       ethnicity=EthnicityLookup.objects.get(id=int(ethnicity)),
                                       race=RaceLookup.objects.get(id=int(race))
                                       )
        d.save()
        
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

    except IntegrityError:
        return JsonResponse(get_error_object(7))

    return JsonResponse(get_success_object())


def update_demographics(request):
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))

    s = Student.objects.get(user=request.user)

    if len(request.POST) is 0:
        return JsonResponse(get_error_object(4))

    if 'age' in request.POST:
        s.age = int(request.POST['age'])

    if 'gender' in request.POST:
        s.gender = GenderLookup.objects.get(id=int(request.POST['gender']))

    if 'grade_year' in request.POST:
        s.gender = GradeYearLookup.objects.get(id=int(request.POST['grade_year']))

    if 'ethnicity' in request.POST:
        s.gender = EthnicityLookup.objects.get(id=int(request.POST['ethnicity']))

    if 'race' in request.POST:
        s.gender = RaceLookup.objects.get(id=int(request.POST['race']))

    s.save()
    return JsonResponse(get_success_object())


def add_position(request):
    is_user_logged_in = request.user.is_authenticated

    if not is_user_logged_in:
        return JsonResponse(get_error_object(0))
    s = Student.objects.get(user=request.user)

    try:
        x = float(request.GET['x'])
        y = float(request.GET['y'])
        p = Position.objects.create(student=s, x=x, y=y)
        p.save()

    except KeyError:
        return JsonResponse(get_error_object(4))

    return JsonResponse(get_success_object())
