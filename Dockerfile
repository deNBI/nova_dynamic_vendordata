FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache build-base linux-headers && pip3 install --no-cache-dir -r requirements.txt && apk del build-base linux-headers

COPY . /usr/src/app

EXPOSE 9000

CMD gunicorn --workers 3 --bind 127.0.0.1:9000 wsgi:app