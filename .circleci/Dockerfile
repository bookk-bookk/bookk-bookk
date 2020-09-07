FROM python:3.8-buster

# Install hadolint for linting Dockerfile
RUN wget -O /bin/hadolint https://github.com/hadolint/hadolint/releases/download/v1.16.3/hadolint-Linux-x86_64 --no-check-certificate
RUN chmod +x /bin/hadolint

# Install pip packages for linting python codes and executing unit tests.
WORKDIR /home/
COPY requirements.txt/ /home/requirements.txt
COPY requirements_local.txt/ /home/requirements_local.txt


RUN pip install --upgrade pip && pip install -r requirements_local.txt

CMD /bin/bash
