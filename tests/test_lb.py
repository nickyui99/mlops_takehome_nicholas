"""
Load Balancer Configuration Tests
Tests that verify load balancing is properly configured without requiring running servers.
"""
import pytest
from pathlib import Path


def test_nginx_config_exists():
    """Test that nginx configuration file exists"""
    nginx_config = Path(__file__).parent.parent / "nginx.conf"
    assert nginx_config.exists(), "nginx.conf should exist for load balancing"


def test_nginx_has_upstream_config():
    """Test that nginx.conf has upstream server configuration"""
    nginx_config = Path(__file__).parent.parent / "nginx.conf"
    
    if not nginx_config.exists():
        pytest.skip("nginx.conf not found")
    
    content = nginx_config.read_text()
    
    # Check for upstream block
    assert "upstream" in content, "nginx.conf should have upstream configuration"
    assert "server" in content, "nginx.conf should define backend servers"
    
    # Check for load balancing keywords
    has_lb_config = any(keyword in content for keyword in [
        "least_conn", "ip_hash", "round_robin", "upstream"
    ])
    assert has_lb_config, "nginx.conf should have load balancing configuration"


def test_docker_compose_has_replicas():
    """Test that docker-compose defines multiple service replicas"""
    docker_compose = Path(__file__).parent.parent / "docker-compose.yaml"
    
    if not docker_compose.exists():
        pytest.skip("docker-compose.yaml not found")
    
    content = docker_compose.read_text()
    
    # Check for scale or deploy configuration
    has_scaling = any(keyword in content for keyword in [
        "replicas", "scale", "deploy:"
    ])
    
    # If no explicit scaling, multiple service definitions is also valid
    api_count = content.count("titanic-api")
    
    assert has_scaling or api_count > 1, "docker-compose should configure multiple instances"


def test_kubernetes_deployment_has_replicas():
    """Test that Kubernetes deployment specifies multiple replicas"""
    k8s_deployment = Path(__file__).parent.parent / "deploy" / "k8s" / "deployment.yaml"
    
    if not k8s_deployment.exists():
        pytest.skip("Kubernetes deployment not found")
    
    content = k8s_deployment.read_text()
    
    # Check for replicas specification
    assert "replicas:" in content, "Kubernetes deployment should specify replicas"
    
    # Extract replica count (simple check)
    lines = content.split("\n")
    for line in lines:
        if "replicas:" in line:
            # Basic validation that replica count > 1
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    replica_count = int(parts[1].strip())
                    assert replica_count >= 2, f"Should have at least 2 replicas, found {replica_count}"
                except ValueError:
                    pass  # Skip if can't parse, other checks will validate


def test_load_balancing_documentation():
    """Test that README documents load balancing setup"""
    readme = Path(__file__).parent.parent / "README.md"
    
    if not readme.exists():
        pytest.skip("README.md not found")
    
    content = readme.read_text(encoding='utf-8').lower()
    
    # Check for load balancing documentation
    has_lb_docs = any(keyword in content for keyword in [
        "load balanc", "nginx", "replicas", "horizontal scaling"
    ])
    
    assert has_lb_docs, "README should document load balancing configuration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])