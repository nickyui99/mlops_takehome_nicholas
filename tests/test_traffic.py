"""
Traffic generation script for testing Grafana metrics.

This script sends multiple prediction requests to the API to generate
metrics data that can be visualized in Grafana dashboards.
"""

import requests
import random
import time
import argparse
from typing import Dict, List
from statistics import mean, median


class TrafficGenerator:
    """Generate traffic to the prediction API for metrics testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    def generate_random_passenger(self) -> Dict:
        """Generate random Titanic passenger data."""
        return {
            "pclass": random.randint(1, 3),
            "sex": random.choice(["male", "female"]),
            "age": float(random.randint(1, 80)),
            "sibsp": random.randint(0, 4),
            "parch": random.randint(0, 4),
            "fare": float(random.uniform(5.0, 300.0)),
            "embarked": random.choice(["C", "Q", "S"])
        }
    
    def send_prediction_request(self, passenger_data: Dict, expect_error: bool = False) -> Dict:
        """Send a prediction request and return the result."""
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                json=passenger_data,
                timeout=5
            )
            
            if expect_error and response.status_code >= 400:
                return {
                    "success": False,
                    "expected_error": True,
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "details": response.text[:200]
                }
            
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "expected_error": expect_error,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def trigger_server_error(self) -> Dict:
        """
        Trigger a 500 error using the test endpoint.
        """
        try:
            response = requests.get(
                f"{self.base_url}/test/error500",
                timeout=5
            )
            
            return {
                "success": False,
                "expected_error": True,
                "error": f"HTTP {response.status_code}",
                "status_code": response.status_code,
                "details": response.text[:200] if response.text else ""
            }
        except requests.exceptions.RequestException as e:
            # If the request itself fails, capture the status code
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            return {
                "success": False,
                "expected_error": True,
                "error": str(e),
                "status_code": status_code
            }
    
    def generate_traffic(self, num_requests: int = 100, delay_ms: int = 50, 
                        error_rate: float = 0.3, verbose: bool = True):
        """
        Generate traffic by sending multiple prediction requests.
        
        Args:
            num_requests: Number of requests to send
            delay_ms: Delay between requests in milliseconds
            error_rate: Percentage of requests that should be errors (0.0-1.0)
            verbose: Print progress information
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"Generating {num_requests} requests to {self.base_url}")
            print(f"Error rate: {error_rate*100:.1f}%")
            print(f"{'='*70}\n")
        
        successful_requests = 0
        failed_requests = 0
        expected_errors = 0
        latencies = []
        error_types_count = {
            "5xx": 0,
            "timeout": 0,
            "connection": 0
        }
        
        for i in range(1, num_requests + 1):
            # Decide if this should be an error request
            should_generate_error = random.random() < error_rate
            
            if should_generate_error:
                result = self.trigger_server_error()
            else:
                passenger = self.generate_random_passenger()
                result = self.send_prediction_request(passenger)
            
            self.results.append(result)
            
            if result["success"]:
                successful_requests += 1
                data = result["data"]
                latency = data.get("latency_ms", 0)
                latencies.append(latency)
                
                if verbose:
                    pod_name = data.get("pod_name", "unknown")[:12]
                    prediction = data.get("prediction", "N/A")
                    probability = data.get("survival_probability", 0)
                    print(f"[{i:3d}/{num_requests}] ✓ Pod: {pod_name} | "
                          f"Prediction: {prediction:8s} | "
                          f"Probability: {probability:.4f} | "
                          f"Latency: {latency:.2f}ms")
            else:
                failed_requests += 1
                if result.get("expected_error"):
                    expected_errors += 1
                
                status_code = result.get("status_code")
                if status_code and 500 <= status_code < 600:
                    error_types_count["5xx"] += 1
                
                if "timeout" in result.get("error", "").lower():
                    error_types_count["timeout"] += 1
                elif "connection" in result.get("error", "").lower():
                    error_types_count["connection"] += 1
                
                if verbose:
                    error = result.get("error", "Unknown error")
                    status = result.get("status_code", "N/A")
                    expected_marker = "⚠" if result.get("expected_error") else "✗"
                    print(f"[{i:3d}/{num_requests}] {expected_marker} Error [{status}]: {error[:50]}")
            
            # Add delay between requests
            if i < num_requests:
                time.sleep(delay_ms / 1000.0)
        
        if verbose:
            print(f"\n{'='*70}")
            print("Traffic Generation Summary")
            print(f"{'='*70}")
            print(f"Total Requests:     {num_requests}")
            print(f"Successful:         {successful_requests} ({successful_requests/num_requests*100:.1f}%)")
            print(f"Failed:             {failed_requests} ({failed_requests/num_requests*100:.1f}%)")
            print(f"  - Expected:       {expected_errors}")
            print(f"  - Unexpected:     {failed_requests - expected_errors}")
            
            if any(error_types_count.values()):
                print(f"\nError Breakdown:")
                if error_types_count["5xx"] > 0:
                    print(f"  - 5xx Errors:     {error_types_count['5xx']}")
                if error_types_count["timeout"] > 0:
                    print(f"  - Timeouts:       {error_types_count['timeout']}")
                if error_types_count["connection"] > 0:
                    print(f"  - Connection:     {error_types_count['connection']}")
            
            if latencies:
                print(f"\nLatency Statistics:")
                print(f"  Mean:             {mean(latencies):.2f}ms")
                print(f"  Median:           {median(latencies):.2f}ms")
                print(f"  Min:              {min(latencies):.2f}ms")
                print(f"  Max:              {max(latencies):.2f}ms")
            
            print(f"\n{'='*70}")
            print("✓ Traffic generation complete!")
            print("  Check Grafana dashboard at: http://localhost:3000")
            print("  Dashboard: Titanic Survival Prediction Dashboard")
            print(f"{'='*70}\n")
        
        return {
            "total": num_requests,
            "successful": successful_requests,
            "failed": failed_requests,
            "expected_errors": expected_errors,
            "error_types": error_types_count,
            "latencies": latencies
        }
    
    def get_health_status(self) -> bool:
        """Check if the API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def main():
    """Main function to run traffic generation."""
    parser = argparse.ArgumentParser(
        description="Generate traffic for Grafana metrics testing"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=1000,
        help="Number of requests to send (default: 100)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=10,
        help="Delay between requests in milliseconds (default: 100)"
    )
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.2,
        help="Percentage of requests that should be errors, 0.0-1.0 (default: 0.2 = 20%%)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate error rate
    if not 0.0 <= args.error_rate <= 1.0:
        print("❌ Error: --error-rate must be between 0.0 and 1.0")
        return 1
    
    # Create traffic generator
    generator = TrafficGenerator(base_url=args.url)
    
    # Check health
    print("Checking API health...")
    if not generator.get_health_status():
        print(f"❌ Error: API at {args.url} is not responding to health checks")
        print("   Make sure the service is running:")
        print("   - Local: docker compose up")
        print("   - Kubernetes: kubectl port-forward svc/titanic-predictor-svc 8000:8000 -n mlops-dev")
        return 1
    
    print("✓ API is healthy\n")
    
    # Generate traffic
    generator.generate_traffic(
        num_requests=args.requests,
        delay_ms=args.delay,
        error_rate=args.error_rate,
        verbose=not args.quiet
    )
    
    return 0


if __name__ == "__main__":
    exit(main())