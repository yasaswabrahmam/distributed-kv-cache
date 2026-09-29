"""
Integration Test & Demo for Distributed KV Cache
"""
import time
import subprocess
import sys
from client import DistributedCacheClient

def run_demo():
    nodes = ["127.0.0.1:8001", "127.0.0.1:8002", "127.0.0.1:8003"]
    client = DistributedCacheClient(nodes)

    print("=" * 60)
    print("DISTRIBUTED KEY-VALUE CACHE CLUSTER DEMO")
    print("Nodes in Ring: 127.0.0.1:8001, 127.0.0.1:8002, 127.0.0.1:8003")
    print("=" * 60)

    test_items = [
        ("user:101", "Yasaswa Brahmam"),
        ("user:102", "Amazon SysDE"),
        ("order:992", "EC2 Compute Instance"),
        ("session:abc", "ACTIVE_TOKEN_99"),
        ("metrics:cpu", "42.5"),
        ("payment:77", "APPROVED")
    ]

    print("\n--- 1. Testing Consistent Hashing Routing (SET) ---")
    for key, val in test_items:
        try:
            res = client.set(key, val)
            print(f"SET {key:<15} -> Routed to {res['routed_to']} [Status: {res['status']}]")
        except ConnectionRefusedError:
            print(f"[!] Node not running. Please start the servers first: python server.py <port>")
            return

    print("\n--- 2. Retrieving Keys (GET) ---")
    for key, _ in test_items:
        res = client.get(key)
        print(f"GET {key:<15} -> From {res['routed_to']} [Value: {res.get('value')}]")

if __name__ == "__main__":
    run_demo()
