from django.http import HttpResponse
import re
#used in middleware.py
def extract_error_message(response: HttpResponse) -> str:
    content = response.content.decode('utf-8')

    if 'validation' in content.lower():
        error_pattern = r'Error=.+!'
        match = re.search(error_pattern, content)
        if match:
            error_code = match.group()
            return error_code.strip('!').split('=')
      
    return None  
