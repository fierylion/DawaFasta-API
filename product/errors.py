from django.http import HttpResponse, JsonResponse
import re
from rest_framework import serializers
#used in middleware.py
def validation_error_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except serializers.ValidationError as exc:
            details = exc.detail
            return JsonResponse({'err': f'{details["id"]} is not a valid id for {details["det"]}'}, status=400)
    
    return wrapper

