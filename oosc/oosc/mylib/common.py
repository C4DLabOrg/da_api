from rest_framework.exceptions import APIException


class MyCustomException(APIException):
    status_code = 503
    detail="Service temporarily unavailable, try again later."
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'

    def __init__(self,message,code):
        self.status_code=code
        self.default_detail=message
        self.detail=message