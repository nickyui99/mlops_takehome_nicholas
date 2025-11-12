import requests

url = "http://localhost:8000/predict"
data = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
headers = {"Content-Type": "application/json"}

for i in range(6):
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        pod = resp.json().get("pod_name", "unknown")
        print(f"Request {i+1} → Pod: {pod}")
    else:
        print("Error:", resp.status_code)