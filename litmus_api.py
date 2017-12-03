import requests

API_ENDPOINT = "https://litmus-app-187901.appspot.com"
SID_FILE = "sid.txt"

def get_sid():
    with open(SID_FILE, "r") as f:
        return f.readline().strip()
API_KEY = get_sid()

def check_state():
    endpoint = API_ENDPOINT + "/sniffer/check_state/" + API_KEY
    r = requests.post(url = endpoint, data = {})
    if r:
        returned = r.json()
        return returned['continue']

    return None

def put_data(people, loudness):
    if check_state():
        endpoint = API_ENDPOINT + "/sniffer/put_data/" + API_KEY
        data = {"people" : people, "loudness" : loudness}
        r = requests.post(url = endpoint, data = data)
    else:
        print("ERROR: not connected")
        return None

def disconnect():
    endpoint = API_ENDPOINT + "/client/disconnect/" + API_KEY
    r = requests.post(url = endpoint, data = {})
    return r

def connect():
    endpoint = API_ENDPOINT + "/client/connect/" + API_KEY
    r = requests.post(url = endpoint, data = {})
    return r

