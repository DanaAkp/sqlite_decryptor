FROM python:3.9.7-slim-buster
ARG FLASK_APP
ARG FLASK_ENV
WORKDIR /app

COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]