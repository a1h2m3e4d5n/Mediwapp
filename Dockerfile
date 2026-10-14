FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/media /app/staticfiles && python manage.py collectstatic --noinput
EXPOSE 3000
CMD sh -c "python manage.py migrate --noinput && gunicorn mediwapp.wsgi:application --bind 0.0.0.0:${PORT:-3000} --workers 2 --timeout 90"
