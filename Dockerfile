FROM python:3
LABEL authors="Yerzhan"

WORKDIR /code

# poetry export -f requirements.txt --output requirements.txt
COPY ./requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . .
