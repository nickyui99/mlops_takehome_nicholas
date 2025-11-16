"""
Simple load balancer test for Docker Compose environment.
For Kubernetes testing with proper load balancing verification, use test_lb_proper.py
"""
import requests
from collections import Counter

# For Docker Compose (NGINX load balancer)
url = "http://localhost:8000/predict"

# For Kubernetes NodePort (uncomment to test K8s)
# url = "http://localhost:30800/predict"

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
print(f"Sending 12 requests to: {url}\n")

pod_names = []

for i in range(12):
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            pod = result.get("pod_name", "unknown")
            prediction = result.get("prediction", "unknown")
            latency = result.get("latency_ms", 0)
            pod_names.append(pod)
            print(f"Request {i+1:2d} → Pod: {pod:30s} | Prediction: {prediction:8s} | Latency: {latency:6.2f}ms")
        else:
            print(f"Request {i+1:2d} → Error: {resp.status_code}")
    except Exception as e:
        print(f"Request {i+1:2d} → Exception: {str(e)[:60]}")

# Summary
if pod_names:
    print("\n" + "="*70)
    print("Load Balancing Summary:")
    print("="*70)
    pod_counts = Counter(pod_names)
    unique_pods = len(pod_counts)
    print(f"Total requests: {len(pod_names)}")
    print(f"Unique pods: {unique_pods}")
    print("\nTraffic distribution:")
    for pod, count in sorted(pod_counts.items()):
        percentage = (count / len(pod_names)) * 100
        print(f"  {pod:30s}: {count:2d} requests ({percentage:5.1f}%)")
    
    if unique_pods >= 3:
        print(f"\n✅ SUCCESS: Load balancer is distributing across {unique_pods} pods!")
    elif unique_pods >= 2:
        print(f"\n⚠️  PARTIAL: Traffic distributed across {unique_pods} pods (expected 3)")
    else:
        print(f"\n❌ WARNING: All traffic went to {unique_pods} pod(s)")
        print("   For Docker Compose: Check NGINX configuration")
        print("   For Kubernetes: Use NodePort (localhost:30800) or test_lb_proper.py")
    print("="*70)
else:
    print("\n❌ No successful requests!")