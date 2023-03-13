from django.http.request import HttpRequest

class LogMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        try:
            print(request.headers)
            return self.get_response(request)
        except Exception as e:
            # if request.user.is_authenticated():
                # Log the user
            path = request.get_full_path() # Get the URL Path
            meta = request.META # Get request meta information
            # Log everything
            raise e# Raise exception again after catching
