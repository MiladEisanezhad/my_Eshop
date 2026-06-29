FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=dummy-secret-key-for-build-only-not-used-in-production
ENV DEBUG=False

WORKDIR /app

# gevent needs these C libraries to compile
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn tailstore.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 2 --worker-class gevent --worker-connections 1000"]
