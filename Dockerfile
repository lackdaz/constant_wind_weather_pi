FROM python:3.9-buster

WORKDIR /app

COPY weather_station /app/weather_station
COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "weather_station"]
CMD ["60"]