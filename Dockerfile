FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# إضافة Gunicorn لتشغيل السيرفر في بيئة الإنتاج
RUN pip install gunicorn

COPY . /app/

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mediwapp.wsgi:application"]
