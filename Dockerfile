FROM python:3.10.1-slim-buster
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app
# Expose port 8000 for the Django app to listen on
EXPOSE 8000

command to start the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
