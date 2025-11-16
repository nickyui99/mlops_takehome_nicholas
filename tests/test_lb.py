import requests

url = "http://localhost:8000/predict"
data = {
    "pclass": 1,
    "sex": "female",
    "age": 29.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 100.0,
    "embarked": "C"
}
headers = {"Content-Type": "application/json"}

print("Testing load balancer distribution across replicas...")
print(f"Sending 6 requests to: {url}\n")

for i in range(6):
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        pod = result.get("pod_name", "unknown")
        prediction = result.get("prediction", "unknown")
        print(f"Request {i+1} → Pod: {pod} | Prediction: {prediction}")
    else:
        print(f"Request {i+1} → Error: {resp.status_code}")