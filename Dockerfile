FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app/onlinestore

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
