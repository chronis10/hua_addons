FROM alpine

ENV LANG C.UTF-8

# Copy data for add-on

COPY app.py /
COPY requirements.txt /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
RUN apk add --no-cache python3
RUN python3 -m pip install -r /requirements.txt
CMD ["python3", "app.py"]