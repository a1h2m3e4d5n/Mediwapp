FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# الأسطر الجديدة لحل مشكلة pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "python manage.py migrate && exec gunicorn --bind 0.0.0.0:${PORT:-10000} mediwapp.wsgi:application"]


