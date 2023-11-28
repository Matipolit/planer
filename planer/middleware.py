from django.http import QueryDict, HttpResponse

class HttpPostTunnelingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META["REQUEST_METHOD"] == "DELETE":
            request.DELETE = request.body
        return self.get_response(request)

    def process_exception(self, request, exception): 
        return HttpResponse("in exception")

