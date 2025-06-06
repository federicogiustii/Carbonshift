import requests

request = {
    "M": "Ciao CarbonShift!",
    "D": "2025-06-06T23:59:59",  # Data mock
    "C": "http://localhost:5001/callback"
}

response = requests.post("http://localhost:5000/request", json=request)
print("Risposta dal sistema:", response.text)