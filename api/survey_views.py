from .models import Class, Student, Survey, SurveyQuestion, SurveyResponse
from .response_functions import Response
from api.auth_views import get_user_logged_in, get_user_by_session

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import uuid

SURVEY_ERRORS = {
    500: 'No logged in user',
    501: 'Wrong request method',
    502: 'Not enough GET data',
    503: 'Not enough POST data',
    504: 'Survey does not exist',
    505: 'Class has no Survey created',
    506: 'Class does not exist',
    507: 'Question does not exist',
    508: 'Response already exists'
}


@csrf_exempt
def survey_get_by_class(request):
    """
        Function Summary: This function is used to get a Survey object by the associated Class object.
        Path: '/api/survey/select'
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Required POST parameters:
            class -- The Class ID of the associated Class object

        Possible Error Codes:
            500, 501, 503, 504, 506

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure that the API call is using POST request.
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(501, SURVEY_ERRORS))

    # Ensure that the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(500, SURVEY_ERRORS))

    # Ensure 'class' is in POST parameters
    if 'class' not in request.POST:
        return JsonResponse(Response.get_error_status(503, SURVEY_ERRORS))

    # Lookup Class objects with 'class' parameter.
    class_lookup = Class.objects.filter(id=request.POST['class'])

    # Ensure that the Class object exists.
    if len(class_lookup) == 0:
        return JsonResponse(Response.get_error_status(506, SURVEY_ERRORS))

    # Find Survey object based on Class object.
    current_class = class_lookup[0]
    survey_lookup = Survey.objects.filter(associated_class=current_class)

    # Ensure Survey object exists.
    if len(survey_lookup) == 0:
        return JsonResponse(Response.get_error_status(504, SURVEY_ERRORS))

    # Add the SurveyQuestions from Survey object.
    current_survey = survey_lookup[0]
    survey_dict = current_survey.to_dict()
    survey_dict['questions'] = []

    for question in SurveyQuestion.objects.filter(survey=current_survey):
        survey_dict['questions'].append(question.to_dict())

    # Return success status with Survey and SurveyQuestion objects.
    success_status = Response.get_success_status()
    success_status['data'] = survey_dict
    return JsonResponse(success_status)


@csrf_exempt
def survey_response_add(request):
    """
        Function Summary: This function is used to add SurveyResponse objects.
        Path: '/api/survey/respond'
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The Session ID of the logged in user

        Required POST Parameters:
            survey -- The Class ID of the associated Class object

        Optional POST Parameters:
            <SURVEYQUESTION_ID> -- The ID of a SurveyQuestion to attach a response to

        Possible Error Codes:
            500, 501, 503, 504

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a "data" JSON object.
    """
    # Ensure the API call is using POST request.
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(501, SURVEY_ERRORS))

    # Ensure the User is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(500, SURVEY_ERRORS))

    # Ensure 'survey' in POST parameters.
    if 'survey' not in request.POST:
        return JsonResponse(Response.get_error_status(503, SURVEY_ERRORS))

    # Lookup Survey objects using provided ID.
    survey_lookup = Survey.objects.filter(id=request.POST['survey'])
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Ensure the Survey exists.
    if len(survey_lookup) == 0:
        return JsonResponse(Response.get_error_status(504, SURVEY_ERRORS))

    # Make a copy of the POST parameters and remove the 'survey' parameter.
    post_data = request.POST.copy()
    del post_data['survey']

    results = {}

    # Parse all the POST data.
    for question_id, question_response in post_data.items():
        # Lookup SurveyQuestion object by ID.
        question_lookup = SurveyQuestion.objects.filter(id=question_id)

        # Ensure the SurveyQuestion object exists.
        if len(question_lookup) == 0:
            results[question_id] = 'Question does not exist'
            continue

        question = question_lookup[0]

        # Ensure there is not already a SurveyResponse for that SurveyQuestion and Student
        response_lookup = SurveyResponse.objects.filter(survey_question=question, student=current_student)
        if len(response_lookup) != 0:
            results[question_id] = 'Response already exists'
        # Create a new SurveyResponse object.
        else:
            new_response = SurveyResponse.objects.create(survey_question=question, student=current_student, response=question_response)
            new_response.save()
            results[question_id] = new_response.to_dict()

    # Return newly created SurveyResponse data.
    success_status = Response.get_success_status()
    success_status['data'] = results
    return JsonResponse(success_status)
