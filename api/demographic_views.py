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
        Function Summary: This function is used to create a new demographic object. A success status will be returned with the new Demographic object's information.
        Path: 'api/demographic/create'
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET parameters:
            session_id -- The Session ID of the user making the request

        Required POST Parameters:
            age -- the age of the user
            gender -- the gender of the user
            grade_year -- the grade year of the user
            ethnicity -- the ethnicity of the user
            race -- the race of the user
            major -- the major of the user

        Possible Error Codes:
            200, 201, 203, 204, 205

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the request is using POST
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    # If the user is not logged in, return an error status
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    # Get the logged in Student
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # If a Demographic object already exists, return an error status
    if len(Demographic.objects.filter(student=current_student)) != 0:
        return JsonResponse(Response.get_error_status(204, DEMO_ERRORS))

    # Try to create a new demographic object. Error status will be returned in the data does not validate.
    try:
        new_demographic = Demographic.objects.create(student=current_student,
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
        Function Summary: This function is used to update an existing demographic object. A success status will be returned with the updated Demographic object's information.
        Path: 'api/demographic/update'
        Request Type: POST
        Required Login: True

        Args:
            request -- the HTTP request made to the url

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Optional Request Parameters:
            age -- The age of the user
            gender -- The gender of the user
            grade_year -- The grade year of the user
            ethnicity -- The ethnicity of the user
            race -- The race of the user
            major -- The major of the user

        Possible Error Codes:
            200, 201, 205, 206

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using POST
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    # Ensure the user is logged in. Return an error status if the user is not logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    # Get the logged in Student object
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Try to get the Demographic object registered to the student. Return an error status if the user has not created a Demographic object yet.
    try:
        demo_instance = Demographic.objects.get(student=current_student)

    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))

    # If the age is provided in POST data, update the age in the Demographic object.
    if 'age' in request.POST:
        demo_instance.age = request.POST['age']

    # If the gender is provided in POST data, update the gender in the Demographic object.
    if 'gender' in request.POST:
        try:
            demo_instance.gender = GenderLookup.objects.get(id=request.POST['gender'])
        except GenderLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    # If the grade_year is provided in POST data, update the grade_year in the Demographic object.
    if 'grade_year' in request.POST:
        try:
            demo_instance.grade_year = GradeYearLookup.objects.get(id=request.POST['grade_year'])
        except GradeYearLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    # If the ethnicity is provided in POST data, update the ethnicity in the Demographic object.
    if 'ethnicity' in request.POST:
        try:
            demo_instance.ethnicity = EthnicityLookup.objects.get(id=request.POST['ethnicity'])
        except EthnicityLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    # If the race is provided in POST data, update the race in the Demographic object.
    if 'race' in request.POST:
        try:
            demo_instance.race = RaceLookup.objects.get(id=request.POST['race'])
        except RaceLookup.DoesNotExist:
            return JsonResponse(Response.get_error_status(205, DEMO_ERRORS))

    # If the major is provided in POST data, update the major in the Demographic object.
    if 'major' in request.POST:
        demo_instance.major = request.POST['major']

    # Save the updated Demographic object and return a success status.
    demo_instance.save()
    success_status = Response.get_success_status()
    success_status['data'] = demo_instance.to_dict()
    return JsonResponse(Response.get_success_status())


@csrf_exempt
def demographic_delete(request):
    """
        Function Summary: This function is used to delete a Demographic object.
        Path: 'api/demographic/delete'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Possible Error Codes:
            200, 201, 206

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
    """
    # Ensure the API call is using GET
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    # Ensure that the user is logged in
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    # Get the Student object
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Try to delete the Demographic object associated with the logged in Student object.
    try:
        demo_instance = Demographic.objects.get(student=current_student)
        demo_instance.delete()
        return JsonResponse(Response.get_success_status())

    # Return an error status if the Demographic object does not exist.
    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))


@csrf_exempt
def demographic_select(request):
    """
        Function Summary: This function is used to get a Student's Demographic information
        Path: 'api/demographic/select'
        Request Type: GET
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Possible Error Codes:
            200, 201, 206

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using GET request.
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    # Ensure the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(200, DEMO_ERRORS))

    # Get the currently logged in Student object.
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Get the Demographic object associated with the Student and return it.
    try:
        demo_instance = Demographic.objects.get(student=current_student)
        object_dict = demo_instance.to_dict()
        success_object = Response.get_success_status()
        success_object['data'] = object_dict
        return JsonResponse(success_object)

    # Return error status if the Demographic object does not exist for the Student.
    except Demographic.DoesNotExist:
        return JsonResponse(Response.get_error_status(206, DEMO_ERRORS))


@csrf_exempt
def demographic_form(request):
    """
        Function Summary": This function is used to build a Demographic form.
        Path: 'api/demographic/form'
        Request Type: GET
        Required Login: False

        Args:
            request -- The request made to the server by the client

        Possible Error Codes:
            201

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using GET request
    if request.method != "GET":
        return JsonResponse(Response.get_error_status(201, DEMO_ERRORS))

    form_values = {}

    # Get all the GenderLookup objects.
    genders = GenderLookup.objects.all()
    form_values['genders'] = [g.to_dict() for g in genders]

    # Get all the GradeYearLookup objects.
    grade_years = GradeYearLookup.objects.all()
    form_values['grade_years'] = [g.to_dict() for g in grade_years]

    # Get all the EthnicityLookup objects.
    ethnicities = EthnicityLookup.objects.all()
    form_values['ethnicities'] = [e.to_dict() for e in ethnicities]

    # Get all the RaceLookup objects.
    races = RaceLookup.objects.all()
    form_values['races'] = [r.to_dict() for r in races]

    # Return all of the values and success status
    success_status = Response.get_success_status()
    success_status['data'] = form_values
    return JsonResponse(success_status)
