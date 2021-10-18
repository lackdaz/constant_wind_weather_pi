FROM python:3.9-buster

WORKDIR /app

COPY src /app

RUN pip3 install -r requirements.txt

CMD ["anemometer.py"]
ENTRYPOINT ["python3"]