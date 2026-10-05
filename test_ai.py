import urllib.request
import urllib.error
import json

URL = "http://127.0.0.1:5000/api/prompt/generate"

def test(name, data):
    print(f"--- {name} ---")
    req = urllib.request.Request(URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            print("Status:", response.status)
            print(json.dumps(json.loads(response.read().decode('utf-8')), indent=2))
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        print(e.read().decode('utf-8'))
    print()

# Test 1: Empty
test("TEST 1: Empty prompt", {"prompt": ""})

# Test 2: Valid prompt
test("TEST 2: Valid prompt", {"prompt": "Create a circuit using a 9V battery, 220 ohm resistor and LED."})
