FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install libffi-dev libssl-dev -y

RUN mkdir /src
WORKDIR /src
ADD requirements.txt /src/
ADD app /src/
ADD omni_wagtail_events /src/
ADD manage.py /src/
ADD tox.ini /src/

RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt
RUN pip install tox

EXPOSE 8000
