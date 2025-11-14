import requests

url = "http://localhost:8000/predict"

# Test data: First-class female passenger (high survival probability)
data = {
    "pclass": 1,
    "sex": "female",
    "age": 29.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 100.0,
    "embarked": "C"
}

print("Testing Titanic prediction API...")
print(f"Input: {data}")
resp = requests.post(url, json=data)
print(f"Response: {resp.json()}")

# Test data: Third-class male passenger (low survival probability)
data2 = {
    "pclass": 3,
    "sex": "male",
    "age": 25.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 7.25,
    "embarked": "S"
}

print(f"\nInput: {data2}")
resp2 = requests.post(url, json=data2)
print(f"Response: {resp2.json()}")
