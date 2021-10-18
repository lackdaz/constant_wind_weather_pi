import requests
import datetime
import json


url = "http://gotwind.live/data"

data = {
    "temperature": 10,
    "windspeed": 42,
    "humidity": 85,
}

res = requests.post(url, json=data)
print(res)
