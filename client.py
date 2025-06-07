import requests
import random

request = {
    "M": "Ciao CarbonShift!",   # Message
    "D": random.randint(0, 4),  # Deadline
    "C": "http://localhost:5001/callback" # Callback
}

response = requests.post("http://localhost:5000/request", json=request)
print("Risposta dal sistema:", response.text)
