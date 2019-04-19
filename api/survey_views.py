from .models import Class, Student, Survey, SurveyQuestion, SurveyResponse, SurveyInstance, SurveyQuestionInstance, \
    SurveyPositionInstance, Position, SurveyEntryInstance
from .response_functions import Response
from api.auth_views import get_user_logged_in, get_user_by_session

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import datetime

SURVEY_ERRORS = {
    500: 'No logged in user',
    501: 'Wrong request method',
    502: 'Not enough GET data',
    503: 'Not enough POST data',
    504: 'Survey does not exist',
    505: 'Class has no Survey created',
    506: 'Class does not exist',
    507: 'Question does not exist',
    508: 'Response already exists',
    509: 'Student does not have access to survey',
    510: 'Survey Instance already exists'
}


@csrf_exempt
def end_session_create_survey_instance(request):
    """
        Function Summary: This function is used to end a Student's session and to create a Survey Instance for them to add responses to.
        Path: '/api/survey/generate
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The session ID of the logged in user

        Required POST Parameters:
            class -- The class from which the student was in during the session

        Possible Error Codes:
            500, 501, 503, 504, 506, 510

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level.
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
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    if len(SurveyInstance.objects.filter(survey=current_survey, student=current_student,
                                         date_generated=datetime.datetime.now().date())) != 0:
        return JsonResponse(Response.get_error_status(510, SURVEY_ERRORS))

    # Create a new SurveyInstance object.
    new_survey_instance = SurveyInstance.objects.create(survey=current_survey, student=current_student)
    new_survey_instance.save()

    # Create SurveyQuestionInstance objects for each question associated with the Survey.
    for question in SurveyQuestion.objects.filter(survey=current_survey):
        new_question_instance = SurveyQuestionInstance.objects.create(survey_instance=new_survey_instance,
                                                                      question=question)
        new_question_instance.save()

    start_time_stamp = datetime.datetime.now().replace(hour=current_class.start_time.hour,
                                              minute=current_class.start_time.minute)
    end_time_stamp = datetime.datetime.now().replace(hour=current_class.end_time.hour,
                                            minute=current_class.end_time.minute)

    # Get all of the positions between the start and end timestamp and create position questions.
    for position in Position.objects.filter(student=current_student, timestamp__lte=end_time_stamp,
                                            timestamp__gte=start_time_stamp):
        new_position_instance = SurveyPositionInstance.objects.create(survey_instance=new_survey_instance,
                                                                      position=position)
        new_position_instance.save()

    return JsonResponse(Response.get_success_status())


@csrf_exempt
def get_all_open_survey_instances(request):
    """
        Function Summary: This function is used to get all of the open SurveyInstance objects for a Student.
        Path: '/api/survey/open_surveys'
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The session ID of the logged in user

        Possible Error Codes:
            500, 501

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a 'data' JSON object.
    """
    # Ensure that the API call is using POST request.
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(501, SURVEY_ERRORS))

    # Ensure that the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(500, SURVEY_ERRORS))

    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Get all of the Survey Instance objects with a question or position without response objects.
    open_surveys = set()
    for survey in SurveyInstance.objects.filter(student=current_student):
        for question in SurveyQuestionInstance.objects.filter(survey_instance=survey):
            if len(SurveyResponse.objects.filter(survey_entry_id=question.id)) == 0:
                open_surveys.add(survey)

        for position in SurveyPositionInstance.objects.filter(survey_instance=survey):
            if len(SurveyResponse.objects.filter(survey_entry_id=position.id)) == 0:
                open_surveys.add(survey)

    success_object = Response.get_success_status()
    success_object['data'] = [x.to_dict() for x in open_surveys]
    return JsonResponse(success_object)


@csrf_exempt
def get_survey_by_id(request):
    """
        Function Summary: This function is used to get the information about a SurveyInstance given an id.
        Path: '/api/survey/get'
        Request Type: POST
        Required Login: True

        Args:
            request -- The request made to the server by the client

        Required GET Parameters:
            session_id -- The session ID of the logged in user

        Required POST Parameters:
            survey_id -- The ID of the SurveyInstance object

        Possible Error Codes:
            500, 501, 503, 504, 509

        Return:
            Type: JSON
            Data: A JSON object with a 'status' at the top level. Will contain a 'data' JSON object.
    """
    # Ensure that the API call is using POST request.
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(501, SURVEY_ERRORS))

    # Ensure that the user is logged in.
    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(500, SURVEY_ERRORS))

    # Ensure 'class' is in POST parameters
    if 'survey_id' not in request.POST:
        return JsonResponse(Response.get_error_status(503, SURVEY_ERRORS))

    survey_lookup = SurveyInstance.objects.filter(id=request.POST['survey_id'])

    if len(survey_lookup) == 0:
        return JsonResponse(Response.get_error_status(504, SURVEY_ERRORS))

    current_survey = survey_lookup[0]
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Check that the Survey object belongs to the student logged in.
    if current_student != current_survey.student:
        return JsonResponse(Response.get_error_status(509, SURVEY_ERRORS))

    # Get all open question instance objects and append it to the question list
    questions = []
    for question_instance in SurveyQuestionInstance.objects.filter(survey_instance=current_survey):
        question_dict = question_instance.to_dict()
        question_dict['question'] = question_instance.question.to_dict()
        questions.append(question_dict)

    # Get all open position instance objects and append it to the position list
    positions = []
    for position_instance in SurveyPositionInstance.objects.filter(survey_instance=current_survey):
        position_dict = position_instance.to_dict()
        position_dict['position'] = position_instance.position.to_dict()
        positions.append(position_dict)

    survey = current_survey.to_dict()

    # Return the survey information
    success_object = Response.get_success_status()
    success_object['data'] = {'survey_instance': survey, 'questions': questions, 'positions': positions}
    return JsonResponse(success_object)


@csrf_exempt
def add_responses_to_survey(request):
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
            survey_id -- The Class ID of the associated Survey Instance object

        Optional POST Parameters:
            <SURVEYQUESTION_ID> -- The ID of a SurveyQuestion to attach a response to

        Possible Error Codes:
            500, 501, 503, 504, 509

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
    if 'survey_id' not in request.POST:
        return JsonResponse(Response.get_error_status(503, SURVEY_ERRORS))

    survey_lookup = SurveyInstance.objects.filter(id=request.POST['survey_id'])

    # Return an error if the survey instance does not exist
    if len(survey_lookup) == 0:
        return JsonResponse(Response.get_error_status(504, SURVEY_ERRORS))

    survey_instance = survey_lookup[0]
    current_student = Student.objects.get(user=get_user_by_session(request.GET['session_id']))

    # Return an error if the survey instance
    if current_student != survey_instance.student:
        return JsonResponse(Response.get_error_status(509, SURVEY_ERRORS))

    # Make a copy of the POST parameters and remove the 'survey' parameter.
    post_data = request.POST.copy()
    del post_data['survey_id']

    data_object = {}

    for entry_id, response in post_data.items():
        response_exists = len(SurveyResponse.objects.filter(survey_entry_id=entry_id)) != 0

        if len(SurveyEntryInstance.objects.filter(id=entry_id)) == 0:
            data_object[entry_id] = "bad id"
            continue

        if response_exists:
            SurveyResponse.objects.get(survey_entry_id=entry_id).response = response
            data_object[entry_id] = "updated"
        else:
            new_response = SurveyResponse.objects.create(survey_entry_id=entry_id, response=response)
            new_response.save()
            data_object[entry_id] = "created"

    success_object = Response.get_success_status()
    success_object['data'] = data_object
    return JsonResponse(success_object)
