from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from api.response_functions import Response
from api.models import Feedback

FEEDBACK_ERRORS = {
    600: 'No logged in user',
    601: 'Wrong request method',
    602: 'Not enough GET data',
    603: 'Not enough POST data',
}

@csrf_exempt
def feedback_create(request):
    """
    Function Summary: This function can be used to create a new Feedback object.
    Path: '/api/feedback/submit'
    Request Type: POST
    Required Login: False

    Args:
        request -- The request made to the server by the client

    Required GET Parameters:
        feedback -- The text feedback from the user

    Possible Error Codes:
        601, 603

    Return:
        Type: JSON
        Data: A JSON object with a 'status' at the top level.
    """
    # Ensure that the API call is using POST request
    if request.method != "POST":
        return JsonResponse(Response.get_error_status(601, FEEDBACK_ERRORS))

    # Ensure the POST parameters have enough data
    if 'feedback' not in request.POST:
        return JsonResponse(Response.get_error_status(603, FEEDBACK_ERRORS))

    # Create new Feedback object
    new_feedback = Feedback.objects.create(feedback=request.POST['feedback'])
    new_feedback.save()
    return JsonResponse(Response.get_success_status())
