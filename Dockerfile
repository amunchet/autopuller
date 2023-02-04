FROM ubuntu:latest

RUN apt update && apt install -y \
    python3 \
    python3-pip

ADD requirements.txt /

RUN pip3 install -r /requirements.txt


CMD ["bash", "-c", "sleep inf"]