# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime deps (pin for reproducibility)
RUN pip install --no-cache-dir boto3==1.40.13 click==8.1.7

# Copy application code
COPY aws_object.py main.py ./

# Create lightweight entrypoint wrapper so we can call `awsctl` inside the container
RUN printf '#!/bin/sh\nexec python /app/main.py "$@"\n' > /usr/local/bin/awsctl \
 && chmod +x /usr/local/bin/awsctl

# Default working dir for user projects (mount your CWD here with -v "$PWD":/work -w /work)
WORKDIR /work

# Default to an interactive shell so users can run `awsctl` themselves without passing env vars
ENTRYPOINT ["/bin/sh"]
CMD ["-l"]
