FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=dummy-secret-key-for-build-only-not-used-in-production
ENV DEBUG=False

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && exec gunicorn tailstore.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class gthread --threads 4"]