FROM amancevice/pandas

ENV LANG C.UTF-8

# Copy data for add-on

COPY app.py /scripts/
COPY requirements.txt /tmp/
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /scripts/
RUN pip install -r /tmp/requirements.txt
WORKDIR /scripts
ENTRYPOINT python app.py