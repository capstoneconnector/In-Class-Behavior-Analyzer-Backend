from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def index(request):
    """
    The function that is returned after the use calls the index of the API path
    Path: 'api/'
    """
    return HttpResponse('API Home')
