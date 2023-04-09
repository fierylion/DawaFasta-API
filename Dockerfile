# Python version
FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/


RUN pip install -r requirements.txt

COPY . /app/

# collect static files
RUN python manage.py collectstatic

# Run the command to start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
