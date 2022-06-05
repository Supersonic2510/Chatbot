import requests
import json

url = "http://localhost:3000"
data = {'msg': 'Hi!!!'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)