FROM python:3.10-slim-buster
#FROM debian:10-slim
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -q --yes --no-install-recommends \
    git ca-certificates build-essential python3-dev libffi-dev \
# python3 python3-pip python3-setuptools\
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
COPY . /tmp/autocommit
RUN pip install /tmp/autocommit \
 && rm -rf /tmp/autocommit
ENTRYPOINT ["/bin/sh", "-c"] 
