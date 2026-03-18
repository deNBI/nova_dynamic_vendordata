FROM python:3.12-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apt update && apt install build-essential -y && pip3 install --no-cache-dir -r requirements.txt && apt remove build-essential -y && apt autoremove -y

COPY wsgi.py  /usr/src/app
COPY denbi /usr/src/app/denbi

EXPOSE 9898

CMD gunicorn --workers 3 --bind 0.0.0.0:9898 wsgi:app