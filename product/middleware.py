import jwt
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework import status
import uuid
from .errors import username_to_id
def is_uuid(id):
    try:
        uuid.UUID(id)
        return True
    except:
        return False

def user_authentication_middleware(get_response):
    def middleware(request):
        if request.path.startswith('/api/v1/user'):
            path_details = request.path.split('/')
            path_id = None if len(path_details) <= 4 else path_details[4]
            if path_id is None:
                return JsonResponse({
                    'err': "Invalid Route"
                }, status=404)
            path_details[4] = username_to_id('user', path_id)
            if not is_uuid(path_details[4]):
                return JsonResponse({'error': 'Invalid Route'}, status=404)
            request.path = '/'.join(path_details)
            if 'Authorization' not in request.headers:
                return JsonResponse({'error': 'User not    authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            token = request.headers['Authorization'].split()[1]
            try:
                #verify token
                decoded = jwt.decode(token, settings.JWT_SECRET, algorithms= ['HS256'])
                if not decoded['user']:
                    raise Exception
                request.userID =  decoded['user_id']
                request.name = decoded['user_name']

                if decoded['user_id'] != path_id:
                    raise Exception
            except:
                return JsonResponse({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        return get_response(request)
    return middleware

def company_authentication_middleware(get_response):
    def middleware(request):
        if request.path.startswith('/api/v1/company'):
            path_details = request.path.split('/')
            path_id = None if len(path_details) <= 4 else path_details[4]
            if path_id is None:
                return JsonResponse({
                    'err': "Invalid Route"
                }, status=404)
            path_details[4] = username_to_id('user', path_id)
            if not is_uuid(path_details[4]):
                return JsonResponse({'error': 'Invalid Route'}, status=404)
            request.path = '/'.join(path_details)
            if 'Authorization' not in request.headers:
                return JsonResponse({'error': 'Company not authenticated, SignUp for a company'}, status=status.HTTP_401_UNAUTHORIZED)
            token = request.headers['Authorization'].split()[1].strip()
            #verification of the token
            
            try:
                decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
                #adding to request object
                if decoded['user']:
                    raise Exception

                request.compID = decoded['company_id']
                request.name = decoded['company_name']
                if decoded['company_id'] != path_id:
                    raise Exception
            
            except Exception as exc:
                return JsonResponse({'error': 'Company not authenticated, SignUp for a company'}, status=status.HTTP_401_UNAUTHORIZED)
        return get_response(request)    
    return middleware  

    






            