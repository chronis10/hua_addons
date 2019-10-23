FROM alpine

ENV LANG C.UTF-8

# Copy data for add-on

COPY app.py /
COPY requirements.txt /tmp/
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
RUN apk add --no-cache python3
RUN python -m pip install -r /tmp/requirements.txt
CMD ["python", "app.py"]