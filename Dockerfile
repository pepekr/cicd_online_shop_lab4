FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

RUN python create_superuser.py

# Збірка статики
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "cicd_online_shop_lab4.wsgi:application", "--bind", "0.0.0.0:8000"]
