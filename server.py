"""
TCP Socket Server for a Cache Node
Usage: python server.py <port>
"""
import json
import socket
import sys
import threading
from lru_cache import LRUCache

def handle_client(conn: socket.socket, cache: LRUCache):
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                request = json.loads(data.decode("utf-8"))
                cmd = request.get("cmd")
                key = request.get("key")
                val = request.get("val")

                response = {"status": "OK"}
                if cmd == "GET":
                    result = cache.get(key)
                    response["value"] = result
                    response["status"] = "OK" if result is not None else "NOT_FOUND"
                elif cmd == "SET":
                    cache.put(key, val)
                    response["status"] = "OK"
                elif cmd == "DEL":
                    success = cache.delete(key)
                    response["status"] = "OK" if success else "NOT_FOUND"
                else:
                    response = {"status": "ERROR", "message": "Unknown command"}

                conn.sendall(json.dumps(response).encode("utf-8"))
            except Exception as e:
                err_resp = {"status": "ERROR", "message": str(e)}
                conn.sendall(json.dumps(err_resp).encode("utf-8"))

def start_server(port: int):
    cache = LRUCache(capacity=500, wal_filepath=f"node_{port}.wal")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", port))
    server.listen(128)
    print(f"[*] Cache Node listening on 127.0.0.1:{port} (Thread-Safe LRU + WAL active)...")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, cache), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[!] Shutting down node gracefully.")
    finally:
        server.close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    start_server(port)
