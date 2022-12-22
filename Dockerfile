FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache build-base linux-headers && pip3 install --no-cache-dir -r requirements.txt && apk del build-base linux-headers

COPY wsgi.py  /usr/src/app
COPY denbi /usr/src/app/denbi

EXPOSE 9898

CMD gunicorn --workers 3 --bind 0.0.0.0:9898 wsgi:app