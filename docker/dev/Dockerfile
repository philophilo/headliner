FROM python:2.7

WORKDIR /app

RUN apt-get update -u && apt-get install -y \
        supervisor \
        netcat

RUN supervisord

COPY requirements.txt /app

RUN pip install -r requirements.txt && \
        pip install gunicorn && \
        pip install gevent 

RUN mkdir -p /root/nltk_data
