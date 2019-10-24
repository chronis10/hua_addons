FROM amancevice/pandas

ENV LANG C.UTF-8

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir --upgrade pip 
RUN pip install -r /tmp/requirements.txt
COPY app.py /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
ENTRYPOINT python app.py