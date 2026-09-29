# Distributed Fault-Tolerant Key-Value Store & Cache

A lightweight, distributed in-memory caching engine built from scratch in Python featuring **Consistent Hashing with Virtual Nodes**, an **LRU Eviction Policy**, and **Write-Ahead Logging (WAL)** for crash recovery.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Client Application        |
                      +--------------+--------------+
                                     |
                          Consistent Hash Ring
                                (MD5)
                 +-------------------+-------------------+
                 |                   |                   |
                 v                   v                   v
        +-----------------+ +-----------------+ +-----------------+
        |  Node 1 (8001)  | |  Node 2 (8002)  | |  Node 3 (8003)  |
        |  +-----------+  | |  +-----------+  | |  +-----------+  |
        |  | LRU Cache |  | |  | LRU Cache |  | |  | LRU Cache |  |
        |  +-----------+  | |  +-----------+  | |  +-----------+  |
        |  |  WAL Log  |  | |  |  WAL Log  |  | |  |  WAL Log  |  |
        |  +-----------+  | |  +-----------+  | |  +-----------+  |
        +-----------------+ +-----------------+ +-----------------+
```

### Key Engineering Features
1. **Consistent Hashing Ring:** Uses MD5 hashing with 100 virtual nodes (vnodes) per physical instance to eliminate hot-spotting and ensure uniform key distribution across servers.
2. **$O(1)$ LRU Cache:** Implements a Doubly Linked List + Hash Map data structure with fine-grained mutex locks (`threading.Lock`) for safe concurrent multi-threaded access.
3. **Write-Ahead Logging (WAL):** Persists all `SET` and `DEL` mutations sequentially to disk before memory confirmation, guaranteeing zero data loss across process restart cycles.
4. **TCP Socket Network Layer:** High-performance TCP client-server protocol with non-blocking network I/O.

---

## Quickstart Guide

### 1. Start the Cluster Nodes
Open 3 separate terminals and run:

```bash
# Terminal 1: Node 1
python server.py 8001

# Terminal 2: Node 2
python server.py 8002

# Terminal 3: Node 3
python server.py 8003
```

### 2. Run the Cluster Client Demo
Open a 4th terminal:

```bash
python test_cluster.py
```

---

## Author
* **Muppalla Yasaswa Brahmam** ([GitHub](https://github.com/yasaswabrahmam) | [LinkedIn](https://linkedin.com/in/yasaswa-brahmam))
