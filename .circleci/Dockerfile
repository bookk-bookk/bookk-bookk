FROM python:3.9.16-buster

# Install hadolint for linting Dockerfile
RUN wget -O /bin/hadolint https://github.com/hadolint/hadolint/releases/download/v1.16.3/hadolint-Linux-x86_64 --no-check-certificate
RUN chmod +x /bin/hadolint

# Install Poetry
RUN apt-get update -y && \
    apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

CMD /bin/bash
