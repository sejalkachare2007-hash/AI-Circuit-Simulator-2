import urllib.request
import urllib.error
import json

URL = "http://127.0.0.1:5000/api/circuit/validate"

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
test("TEST 1: Empty circuit", {"components": [], "connections": []})

# Test 2: Battery only
test("TEST 2: Battery only", {
    "components": [
        {"id": "B1", "type": "Battery"}
    ],
    "connections": []
})

# Test 3: Battery to resistor (unconnected pins)
test("TEST 3: Battery positive to resistor", {
    "components": [
        {"id": "B1", "type": "Battery"},
        {"id": "R1", "type": "Resistor"}
    ],
    "connections": [
        {"id": "wire_1", "source": "B1", "sourcePin": "positive", "target": "R1", "targetPin": "pin1"}
    ]
})

# Test 4: Valid structurally
test("TEST 4: Valid circuit (Battery -> Resistor -> LED -> Battery)", {
    "components": [
        {"id": "B1", "type": "Battery"},
        {"id": "R1", "type": "Resistor"},
        {"id": "LED1", "type": "LED"}
    ],
    "connections": [
        {"id": "w1", "source": "B1", "sourcePin": "positive", "target": "R1", "targetPin": "pin1"},
        {"id": "w2", "source": "R1", "sourcePin": "pin2", "target": "LED1", "targetPin": "anode"},
        {"id": "w3", "source": "LED1", "sourcePin": "cathode", "target": "B1", "targetPin": "negative"}
    ]
})

# Test 5: Battery short
test("TEST 5: Battery Short", {
    "components": [
        {"id": "B1", "type": "Battery"}
    ],
    "connections": [
        {"id": "w1", "source": "B1", "sourcePin": "positive", "target": "B1", "targetPin": "negative"}
    ]
})

# Test 6: LED directly across battery
test("TEST 6: LED across battery", {
    "components": [
        {"id": "B1", "type": "Battery"},
        {"id": "LED1", "type": "LED"}
    ],
    "connections": [
        {"id": "w1", "source": "B1", "sourcePin": "positive", "target": "LED1", "targetPin": "anode"},
        {"id": "w2", "source": "B1", "sourcePin": "negative", "target": "LED1", "targetPin": "cathode"}
    ]
})

# Test 7: Duplicate wire
test("TEST 7: Duplicate wire", {
    "components": [
        {"id": "B1", "type": "Battery"},
        {"id": "R1", "type": "Resistor"}
    ],
    "connections": [
        {"id": "w1", "source": "B1", "sourcePin": "positive", "target": "R1", "targetPin": "pin1"},
        {"id": "w2", "source": "B1", "sourcePin": "positive", "target": "R1", "targetPin": "pin1"}
    ]
})

# Test 8: Invalid pin
test("TEST 8: Invalid pin", {
    "components": [
        {"id": "R1", "type": "Resistor"}
    ],
    "connections": [
        {"id": "w1", "source": "R1", "sourcePin": "pin5", "target": "R1", "targetPin": "pin2"}
    ]
})

# Test 9: Self connection
test("TEST 9: Self connection", {
    "components": [
        {"id": "R1", "type": "Resistor"}
    ],
    "connections": [
        {"id": "w1", "source": "R1", "sourcePin": "pin1", "target": "R1", "targetPin": "pin1"}
    ]
})
