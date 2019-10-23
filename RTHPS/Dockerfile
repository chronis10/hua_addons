FROM amancevice/pandas-alpine

ENV LANG C.UTF-8

# Copy data for add-on

COPY run.sh /scripts/
COPY app.py /scripts/
COPY requirements.txt /tmp/
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /scripts/
RUN chmod +x /scripts/run.sh
CMD [ "/scripts/run.sh" ]