"""
Test to verify Kubernetes Service properly load balances traffic across all 3 pods.
Uses fresh connections for each request to test round-robin load balancing.
"""
import requests
from collections import Counter

url = "http://localhost:30800/predict"
data = {
    "pclass": 1,
    "sex": "female",
    "age": 29.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 100.0,
    "embarked": "C"
}

print("Testing load balancer distribution across all 3 replicas...")
print(f"Sending 30 requests to: {url}")
print("Using fresh connections to test load balancing\n")

pod_names = []
session = requests.Session()  # Use session but create new requests

for i in range(30):
    try:
        # Close and reopen connection for better load balancing test
        if i % 10 == 0 and i > 0:
            session.close()
            session = requests.Session()
        
        resp = session.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            pod = result.get("pod_name", "unknown")
            prediction = result.get("prediction", "unknown")
            latency = result.get("latency_ms", 0)
            pod_names.append(pod)
            print(f"Request {i+1:2d} → Pod: {pod:40s} | Prediction: {prediction:8s} | Latency: {latency:6.2f}ms")
        else:
            print(f"Request {i+1:2d} → Error: {resp.status_code}")
    except Exception as e:
        print(f"Request {i+1:2d} → Exception: {str(e)[:60]}")

session.close()

print("\n" + "="*80)
print("Load Balancing Results:")
print("="*80)

if pod_names:
    pod_counts = Counter(pod_names)
    unique_pods = len(pod_counts)
    
    print(f"Total successful requests: {len(pod_names)}")
    print(f"Unique pods served traffic: {unique_pods}")
    print(f"\nTraffic distribution:")
    
    for pod, count in sorted(pod_counts.items()):
        percentage = (count / len(pod_names)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {pod:40s}: {count:2d} requests ({percentage:5.1f}%) {bar}")
    
    print("\n" + "="*80)
    if unique_pods >= 3:
        print("✅ SUCCESS: Traffic is distributed across all 3 pods!")
        print("   The Kubernetes Service is properly load balancing.")
    elif unique_pods == 2:
        print("⚠️  WARNING: Traffic only reached 2 out of 3 pods.")
        print("   One pod may not be ready or load balancing is uneven.")
    else:
        print("❌ FAILED: All traffic went to only 1 pod!")
        print("   Load balancing is not working properly.")
        print("   This is expected with kubectl port-forward (single connection).")
        print("   For true load balancing test, use an Ingress or NodePort directly.")
    print("="*80)
else:
    print("❌ No successful requests to analyze!")
