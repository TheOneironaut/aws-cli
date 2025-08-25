# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN pip install --no-cache-dir boto3==1.40.13 click==8.1.7
COPY aws_object.py main.py ./
RUN printf '#!/bin/sh\nexec python /app/main.py "$@"\n' > /usr/local/bin/awsctl \
 && chmod +x /usr/local/bin/awsctl
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/awsctl"]
CMD ["--help"]
