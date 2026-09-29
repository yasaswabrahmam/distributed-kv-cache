"""
Distributed Cluster Client with Client-Side Consistent Hashing
"""
import json
import socket
from hash_ring import ConsistentHashRing

class DistributedCacheClient:
    def __init__(self, nodes: list[str]):
        self.ring = ConsistentHashRing(replicas=100)
        self.nodes = nodes
        for node in nodes:
            self.ring.add_node(node)

    def _send_command(self, host: str, port: int, payload: dict) -> dict:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(payload).encode("utf-8"))
            data = s.recv(4096)
            return json.loads(data.decode("utf-8"))

    def set(self, key: str, value: str) -> dict:
        target_node = self.ring.get_node(key)
        host, port = target_node.split(":")
        res = self._send_command(host, int(port), {"cmd": "SET", "key": key, "val": value})
        res["routed_to"] = target_node
        return res

    def get(self, key: str) -> dict:
        target_node = self.ring.get_node(key)
        host, port = target_node.split(":")
        res = self._send_command(host, int(port), {"cmd": "GET", "key": key})
        res["routed_to"] = target_node
        return res

    def delete(self, key: str) -> dict:
        target_node = self.ring.get_node(key)
        host, port = target_node.split(":")
        res = self._send_command(host, int(port), {"cmd": "DEL", "key": key})
        res["routed_to"] = target_node
        return res
