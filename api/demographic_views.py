from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.auth_views import get_user_logged_in, get_user_by_session
from api.models import *

from api.response_functions import Response

DEMO_ERRORS = {
    200: 'No session_id in parameters of url',
    201: 'Wrong request type',
    202: 'Not enough GET data',
    203: 'Not enough POST data',
    204: 'Demographic object already exists',
    205: 'Bad lookup value',
    206: 'Demographic object does not exist'
}


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
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    if request.method != "POST":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    if len(Demographic.objects.filter(student=s)) != 0:
        return JsonResponse(Response.get_error_status(204, DEMO_ERRORS))

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
        success_status = Response.get_success_status()
        success_status['data'] = new_demographic.to_dict()
        return JsonResponse(Response.get_success_status())

    except KeyError:
        return JsonResponse(Response.get_error_status(203, DEMO_ERRORS))

    except GenderLookup.DoesNotExist:
        return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    except GradeYearLookup.DoesNotExist:
        return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    except EthnicityLookup.DoesNotExist:
        return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    except RaceLookup.DoesNotExist:
        return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))


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
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    if request.method != "POST":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        demo_instance = Demographic.objects.get(student=s)

    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))

    if 'age' in request.POST:
        demo_instance.age = request.POST['age']

    if 'gender' in request.POST:
        try:
            demo_instance.gender = GenderLookup.objects.get(id=request.POST['gender'])
        except GenderLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    if 'grade_year' in request.POST:
        try:
            demo_instance.grade_year = GradeYearLookup.objects.get(id=request.POST['grade_year'])
        except GradeYearLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    if 'ethnicity' in request.POST:
        try:
            demo_instance.ethnicity = EthnicityLookup.objects.get(id=request.POST['ethnicity'])
        except EthnicityLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    if 'race' in request.POST:
        try:
            demo_instance.race = RaceLookup.objects.get(id=request.POST['race'])
        except RaceLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    if 'major' in request.POST:
        demo_instance.major = request.POST['major']

    demo_instance.save()
    success_status = Response.get_success_status()
    success_status['data'] = demo_instance.to_dict()
    return JsonResponse(Response.get_success_status())


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
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    current_student = get_user_by_session(request.GET['session_id'])

    try:
        demo_instance = Demographic.objects.get(student=current_student)
        demo_instance.delete()
        return JsonResponse(Response.get_success_status())

    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))


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
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    s = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    try:
        demo_instance = Demographic.objects.get(student=s)
        object_dict = demo_instance.to_dict()
        success_object = Response.get_success_status()
        success_object['data'] = object_dict
        return JsonResponse(success_object)

    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))


@csrf_exempt
def demographic_form(request):
    form_values = {}

    genders = GenderLookup.objects.all()
    form_values['genders'] = [{'id': g.id, 'name': g.name} for g in genders]

    grade_years = GradeYearLookup.objects.all()
    form_values['grade_years'] = [{'id': g.id, 'name': g.name} for g in grade_years]

    ethnicities = EthnicityLookup.objects.all()
    form_values['ethnicities'] = [{'id': e.id, 'name': e.name} for e in ethnicities]

    races = RaceLookup.objects.all()
    form_values['races'] = [{'id': r.id, 'name': r.name} for r in races]

    success_status = Response.get_success_status()
    success_status['data'] = form_values
    return JsonResponse(success_status)