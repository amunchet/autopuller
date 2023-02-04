FROM ubuntu:latest

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    docker-compose \
    docker.io

ADD requirements.txt /

RUN pip3 install -r /requirements.txt


CMD ["bash", "-c", "cd /src && /usr/bin/python3 puller.py"]