from .models import Class, Student, Survey, SurveyQuestion, SurveyResponse
from .response_functions import Response
from api.auth_views import get_user_logged_in, get_user_by_session

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

SURVEY_ERRORS = {
    500: 'No logged in user',
    501: 'Wrong request method',
    502: 'Not enough GET data',
    503: 'Not enough POST data',
    504: 'Survey does not exist',
    505: 'Class has no Survey created',
    506: 'Class does not exist'
}


@csrf_exempt
def survey_get_by_class(request):
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(501, SURVEY_ERRORS))

    if not get_user_logged_in(request):
        return JsonResponse(Response.get_error_status(500, SURVEY_ERRORS))

    if 'class' not in request.POST:
        return JsonResponse(Response.get_error_status(503, SURVEY_ERRORS))

    class_lookup = Class.objects.filter(id=request.POST['class'])

    if len(class_lookup) == 0:
        return JsonResponse(Response.get_error_status(506, SURVEY_ERRORS))

    current_class = class_lookup[0]
    survey_lookup = Survey.objects.filter(associated_class=current_class)

    if len(survey_lookup) == 0:
        return JsonResponse(Response.get_error_status(504, SURVEY_ERRORS))

    current_survey = survey_lookup[0]
    survey_dict = current_survey.to_dict()
    survey_dict['questions'] = []

    for question in SurveyQuestion.objects.filter(survey=current_survey):
        survey_dict['questions'].append(question.to_dict())

    success_status = Response.get_success_status()
    success_status['data'] = survey_dict
    return JsonResponse(success_status)
