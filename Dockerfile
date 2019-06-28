FROM python:slim

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY bot /app
WORKDIR /app
RUN mkdir -p db

CMD ["python","script.py"]