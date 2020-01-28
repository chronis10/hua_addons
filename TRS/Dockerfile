FROM python:3

ENV LANG C.UTF-8

COPY requirements.txt /tmp/
RUN apt-get update && apt-get install -y python-pip
RUN pip install -r /tmp/requirements.txt
COPY main.py /
COPY README.md /
COPY logo.png /
CMD [ "python", "./main.py" ]