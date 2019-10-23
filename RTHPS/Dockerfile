FROM amancevice/pandas

ENV LANG C.UTF-8

# Copy data for add-on

COPY run.sh /
COPY app.py /
COPY requirements.txt /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
RUN python3 -m pip install -r requirements.txt
CMD [ "python3rr", "./my_script.py" ]
