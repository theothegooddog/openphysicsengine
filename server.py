r"""
  ___  ____  _____   ____  _____ ______     _______ ____
 / _ \|  _ \| ____| / ___|| ____|  _ \ \   / / ____|  _ \
| | | | |_) |  _|   \___ \|  _| | |_) \ \ / /|  _| | |_) |
| |_| |  __/| |___   ___) | |___|  _ < \ V / | |___|  _ <
 \___/|_|   |_____| |____/|_____|_| \_\ \_/  |_____|_| \_\

Open-Physics multiplayer server.

Stores player data (position, velocity, rotation, size, name) for every
connected client and relays the full world state back to everyone.

Protocol: newline-delimited JSON over TCP.

  client -> server  {"type": "hello",  "name": "alice"}
  client -> server  {"type": "update", "player": {"Position": [...], ...}}
  server -> client  {"type": "welcome", "id": 3}
  server -> client  {"type": "state",   "players": {"1": {...}, "2": {...}}}

Run:  python server.py [--host 0.0.0.0] [--port 5555]
"""

### LIBRARIES ###
import socket
import threading
import json
import argparse
from time import time, sleep

### GLOBALS ###

DEFAULT_HOST = "0.0.0.0"   # listen on every interface so LAN clients can reach us
DEFAULT_PORT = 5555
BROADCAST_HZ = 30          # how often the world snapshot is pushed to clients
RECV_SIZE = 4096


### PLAYER STORE ###


class PlayerStore:
	"""Thread-safe container for all connected players' data."""

	def __init__(self):
		self._players = {}
		self._lock = threading.Lock()
		self._next_id = 1

	def add(self):
		with self._lock:
			pid = self._next_id
			self._next_id += 1
			self._players[pid] = {
			 "id": pid,
			 "name": f"player{pid}",
			 "Position": [0, 0, 0],
			 "Velocity": [0, 0, 0],
			 "Rotation": [0, 0, 0],
			 "Size": [2, 2, 2],
			 "last_seen": time(),
			}
			return pid

	def update(self, pid, data):
		# Only let clients overwrite known, safe fields.
		allowed = ("name", "Position", "Velocity", "Rotation", "Size")
		with self._lock:
			player = self._players.get(pid)
			if player is None:
				return
			for key in allowed:
				if key in data:
					player[key] = data[key]
			player["last_seen"] = time()

	def remove(self, pid):
		with self._lock:
			self._players.pop(pid, None)

	def snapshot(self):
		with self._lock:
			# String keys so the dict survives the JSON round-trip cleanly.
			return {str(pid): dict(p) for pid, p in self._players.items()}


### CLIENT CONNECTION ###


class ClientConn:
	"""Wraps a single client socket with its own send lock."""

	def __init__(self, conn, addr, pid):
		self.conn = conn
		self.addr = addr
		self.pid = pid
		self.alive = True
		self._send_lock = threading.Lock()

	def send(self, obj):
		line = (json.dumps(obj) + "\n").encode()
		with self._send_lock:
			try:
				self.conn.sendall(line)
			except OSError:
				self.alive = False

	def close(self):
		self.alive = False
		try:
			self.conn.close()
		except OSError:
			pass


### SERVER ###


class Server:

	def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
		self.host = host
		self.port = port
		self.store = PlayerStore()
		self.clients = {}          # pid -> ClientConn
		self.clients_lock = threading.Lock()
		self._running = False
		self._sock = None

	### connection lifecycle ###

	def start(self):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.bind((self.host, self.port))
		self._sock.listen()
		self._running = True

		threading.Thread(target=self._broadcast_loop, daemon=True).start()

		print(f"[OPE] server listening on {self.host}:{self.port}")
		try:
			while self._running:
				conn, addr = self._sock.accept()
				threading.Thread(
				 target=self._handle_client, args=(conn, addr), daemon=True
				).start()
		except KeyboardInterrupt:
			print("\n[OPE] shutting down")
		finally:
			self.stop()

	def stop(self):
		self._running = False
		with self.clients_lock:
			for client in list(self.clients.values()):
				client.close()
			self.clients.clear()
		if self._sock:
			try:
				self._sock.close()
			except OSError:
				pass

	### per-client handling ###

	def _handle_client(self, conn, addr):
		pid = self.store.add()
		client = ClientConn(conn, addr, pid)
		with self.clients_lock:
			self.clients[pid] = client

		client.send({"type": "welcome", "id": pid})
		print(f"[OPE] player {pid} connected from {addr[0]}:{addr[1]}")

		buf = ""
		try:
			while self._running and client.alive:
				data = conn.recv(RECV_SIZE)
				if not data:
					break
				buf += data.decode(errors="ignore")
				while "\n" in buf:
					line, buf = buf.split("\n", 1)
					line = line.strip()
					if line:
						self._handle_message(pid, line)
		except OSError:
			pass
		finally:
			self._disconnect(pid)

	def _handle_message(self, pid, line):
		try:
			msg = json.loads(line)
		except json.JSONDecodeError:
			return
		mtype = msg.get("type")
		if mtype == "hello":
			name = msg.get("name")
			if isinstance(name, str) and name:
				self.store.update(pid, {"name": name})
		elif mtype == "update":
			player = msg.get("player")
			if isinstance(player, dict):
				self.store.update(pid, player)

	def _disconnect(self, pid):
		self.store.remove(pid)
		with self.clients_lock:
			client = self.clients.pop(pid, None)
		if client:
			client.close()
		print(f"[OPE] player {pid} disconnected")

	### broadcasting ###

	def _broadcast_loop(self):
		while self._running:
			sleep(1 / BROADCAST_HZ)
			snapshot = self.store.snapshot()
			message = {"type": "state", "players": snapshot}
			with self.clients_lock:
				targets = list(self.clients.values())
			dead = []
			for client in targets:
				client.send(message)
				if not client.alive:
					dead.append(client.pid)
			for pid in dead:
				self._disconnect(pid)


### MAIN ###


def parse_args():
	parser = argparse.ArgumentParser(description="Open-Physics multiplayer server")
	parser.add_argument("--host", default=DEFAULT_HOST,
	                    help=f"interface to bind (default {DEFAULT_HOST})")
	parser.add_argument("--port", type=int, default=DEFAULT_PORT,
	                    help=f"port to listen on (default {DEFAULT_PORT})")
	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	Server(host=args.host, port=args.port).start()
