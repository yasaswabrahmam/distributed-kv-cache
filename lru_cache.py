"""
Thread-Safe In-Memory LRU Cache with Write-Ahead Logging (WAL)
"""
import os
import threading
from typing import Any, Optional

class Node:
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None

class LRUCache:
    def __init__(self, capacity: int = 1000, wal_filepath: str = "wal.log"):
        self.capacity = capacity
        self.wal_filepath = wal_filepath
        self.cache: dict[str, Node] = {}
        self.lock = threading.Lock()

        # Dummy head and tail nodes for Doubly Linked List
        self.head = Node("__HEAD__", None)
        self.tail = Node("__TAIL__", None)
        self.head.next = self.tail
        self.tail.prev = self.head

        # Replay WAL if it exists to recover state
        self._recover_from_wal()

    def _add_node(self, node: Node):
        """Add node right after head (most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node):
        """Remove an existing node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _move_to_head(self, node: Node):
        """Move an accessed node to head (mark as most recently used)."""
        self._remove_node(node)
        self._add_node(node)

    def _pop_tail(self) -> Node:
        """Evict the least recently used node."""
        res = self.tail.prev
        self._remove_node(res)
        return res

    def _append_wal(self, op: str, key: str, val: Any = ""):
        """Append write operations to disk before updating memory."""
        try:
            with open(self.wal_filepath, "a") as f:
                f.write(f"{op}|{key}|{val}\n")
        except Exception as e:
            print(f"[WAL Error] Failed to write log: {e}")

    def _recover_from_wal(self):
        """Replay WAL logs upon node startup."""
        if not os.path.exists(self.wal_filepath):
            return
        print(f"[*] Replaying WAL from {self.wal_filepath}...")
        with open(self.wal_filepath, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    op, key = parts[0], parts[1]
                    val = parts[2] if len(parts) > 2 else None
                    if op == "SET":
                        self._put_in_memory(key, val)
                    elif op == "DEL":
                        self._del_in_memory(key)

    def _put_in_memory(self, key: str, value: Any):
        node = self.cache.get(key)
        if not node:
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            if len(self.cache) > self.capacity:
                tail = self._pop_tail()
                del self.cache[tail.key]
        else:
            node.value = value
            self._move_to_head(node)

    def _del_in_memory(self, key: str) -> bool:
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            del self.cache[key]
            return True
        return False

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            node = self.cache.get(key)
            if not node:
                return None
            self._move_to_head(node)
            return node.value

    def put(self, key: str, value: Any):
        with self.lock:
            self._append_wal("SET", key, value)
            self._put_in_memory(key, value)

    def delete(self, key: str) -> bool:
        with self.lock:
            self._append_wal("DEL", key)
            return self._del_in_memory(key)
