FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /core

RUN apt update && apt upgrade -y && apt install -y libpq-dev build-essential --fix-missing && apt clean



COPY requirements.txt /core/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /core/

EXPOSE 5000

CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
