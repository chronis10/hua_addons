ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Copy data for add-on

COPY run.sh /
COPY app.py /
COPY requirements.txt /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
RUN chmod a+x /run.sh
RUN apk add --no-cache python3
RUN python3 -m pip install -r requirements.txt
CMD [ "/run.sh" ]
