from django.http import HttpResponse, JsonResponse
import re
from rest_framework import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date
from functools import wraps
#used in middleware.py
def validation_error_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except serializers.ValidationError as exc:
            details = exc.detail
            id = details.get('id', None)
            field= details.get('det', None)
            if(not(id or field)):
                return JsonResponse(details, status=400)
            return JsonResponse({'err': f'{id} is not a valid id for {field}'}, status=400)
    
    return wrapper

#custom encoder to avoid object of type date not serializable by json.dumps of loeader yamls file 
def customJSONEncoder(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


