FROM amancevice/pandas

ENV LANG C.UTF-8

# Copy data for add-on

COPY app.py /
COPY requirements.txt /
COPY README.md /
COPY logo.png /
COPY recommendation_status.py /
RUN pip install Flask
CMD ["python", "app.py"]