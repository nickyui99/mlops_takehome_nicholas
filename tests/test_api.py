import requests

url = "http://localhost:8000/predict"
data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}
resp = requests.post(url, json=data)
print(resp.json())
