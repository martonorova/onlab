FROM python:3.6
RUN mkdir /code
ADD . /code
WORKDIR /code

EXPOSE 8000

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv lock
RUN pipenv install