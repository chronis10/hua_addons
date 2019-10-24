FROM ubuntu

ENV LANG C.UTF-8

COPY requirements.txt /tmp/
RUN apt-get update && apt-get install -y python-pip
RUN pip install -r /tmp/requirements.txt
COPY app.py /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
ENTRYPOINT python app.py