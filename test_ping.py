import urllib.request
import json

for host in ["localhost", "127.0.0.1"]:
    url = f"http://{host}:8000/"
    try:
        with urllib.request.urlopen(url) as response:
            print(f"Ping {url} succeeded: code {response.code}")
    except Exception as e:
        print(f"Ping {url} failed: {str(e)}")
