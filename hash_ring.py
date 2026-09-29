"""
Consistent Hashing Ring with Virtual Nodes
"""
import bisect
import hashlib

class ConsistentHashRing:
    def __init__(self, replicas: int = 100):
        self.replicas = replicas  # Virtual nodes per physical node
        self.ring: dict[int, str] = {}  # Hash value -> physical node identifier
        self.sorted_keys: list[int] = []  # Sorted ring positions

    def _hash(self, key: str) -> int:
        """MD5 32-bit integer hash."""
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) & 0xFFFFFFFF

    def add_node(self, node: str):
        """Add a physical node by creating virtual replicas on the ring."""
        for i in range(self.replicas):
            vnode_key = f"{node}#vnode-{i}"
            hash_val = self._hash(vnode_key)
            self.ring[hash_val] = node
            bisect.insort(self.sorted_keys, hash_val)

    def remove_node(self, node: str):
        """Remove a physical node and its virtual replicas."""
        for i in range(self.replicas):
            vnode_key = f"{node}#vnode-{i}"
            hash_val = self._hash(vnode_key)
            if hash_val in self.ring:
                del self.ring[hash_val]
                self.sorted_keys.remove(hash_val)

    def get_node(self, key: str) -> str:
        """Determine which node holds the given key."""
        if not self.ring:
            raise ValueError("Hash ring is empty. Add nodes first.")

        hash_val = self._hash(key)
        # Binary search for the first virtual node >= hash_val
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        
        # If we reached the end of the ring, wrap around to the first node
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]
