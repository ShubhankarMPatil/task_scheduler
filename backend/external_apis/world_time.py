import requests


def fetch_current_time():
    response = requests.get("https://worldtimeapi.org/api/ip", timeout=5)
    response.raise_for_status()
    return response.json()
