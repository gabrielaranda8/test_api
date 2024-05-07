FROM python:3.10-slim-buster

ADD . /api_challenge
WORKDIR /api_challenge

RUN pip install -r requirements.txt

CMD [ "python", "./app.py"]