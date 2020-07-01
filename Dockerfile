FROM python:3.8-buster

RUN mkdir -p /home/bookk-bookk
COPY . /home/bookk-bookk
WORKDIR /home/bookk-bookk

RUN pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements/prod.txt

EXPOSE 8000

ENTRYPOINT gunicorn -c gunicorn.ini.py app:app
