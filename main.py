"""
  ___  ____  _____ _   _       ____  _   ___   ______ ___ ____ ____  
 / _ \|  _ \| ____| \ | |     |  _ \| | | \ \ / / ___|_ _/ ___/ ___| 
| | | | |_) |  _| |  \| |_____| |_) | |_| |\ V /\___ \| | |   \___ \ 
| |_| |  __/| |___| |\  |_____|  __/|  _  | | |  ___) | | |___ ___) |
 \___/|_|   |_____|_| \_|     |_|   |_| |_| |_| |____/___\____|____/ 

Open-Physics is an open-source physics engine.
Repo: https://github.com/theothegooddog/openphysicsengine

"""

### LIBRARIES ###
from enum import Enum
from time import sleep
from math import floor as mfloor
import turtle as t
import socket
import threading
import json
import argparse

### GLOBALS ###

FPS = 30
TICK = 0
LIBRARY_MODE = bool(__name__ != "__main__")

### HELPERS ###


class MathEnum():
	Huge = 10**1000
	Min = 1 / (10**20)


class Property(Enum):
	Gravity = "Gravity"
	Mass = "Mass"
	Position = "Position"
	Velocity = "Velocity"
	Restitution = "Restitution"
	Friction = "Friction"
	AirResistance = "Air Resistance"
	Anchored = "Anchored"
	Size = "Size"

	@staticmethod
	def from_string(name: str):
		if not isinstance(name, str):
			raise TypeError(f"Expected str, got {type(name).__name__}")
		try:
			return Property(name)
		except ValueError:
			raise ValueError(f"Unknown property: {name}")


def prop(name: str) -> Property:
	return Property.from_string(name)


class ObjectType(Enum):
	Point = "point"
	Floor = "floor"
	Camera = "camera"
	Player = "player"

	@staticmethod
	def from_string(name: str):
		if not isinstance(name, str):
			raise TypeError(f"Expected str, got {type(name).__name__}")
		try:
			return ObjectType(name.lower())
		except ValueError:
			raise ValueError(f"Unknown type: {name}")


def objt(name: str) -> ObjectType:
	return ObjectType.from_string(name)


class Workspace:

	def __init__(self):
		self.Gravity = 0.5
		self.Objects = {}
		self.GravityDirection = (0, -1, 0)
		self.AirResistance = 0.003
		self.Floor = None

	def addObject(self, obj):
		if obj.Type == "Floor": self.Floor = obj
		else:
			uuid = len(self.Objects) + 1
			self.Objects[uuid] = obj
			obj.uuid = uuid
			obj.workspace = self
			return uuid

	def addObjects(self, *objs):
		for obj in objs:
			addObject(obj)

	def getObject(self, uuid):
		return self.Objects[uuid]

	def getAllObjects(self):
		return self.Objects

	def getGlobalTime(self):
		return mfloor(TICK / FPS * 100) / 100

	def getFloor(self):
		return self.Floor

	def setProperty(self, property: Property, value):
		if property == Property.Gravity:
			if type(value).__name__ == "int":
				self.Gravity = value
				return True, f"Set gravity to {value}"
		if property == Property.AirResistance:
			if type(value).__name__ == "float":
				self.AirResistance = value
				return True, f"Set Air Resistance to {value}"
		else:
			return (False, None)

	def getProperty(self, property: Property):
		if property == Property.Gravity: return True, self.Gravity
		elif property == Property.AirResistance: return True, self.AirResistance
		else: return (False, None)


class Object:

	def __init__(self):
		self.Mass = 0
		self.Restitution = 0
		self.Friction = 0
		self.Position = [0, 0, 0]
		self.Velocity = [0, 0, 0]
		self.Size = [
		 0, 0, 0
		]  #Note for rendering: Size is [width, height, length] or [x, y, z]
		self.Anchored = True
		self.workspace = None
		self.uuid = None
		self.Type = None
		self._listeners = {}

	def create(self, type: ObjectType):
		type = str(type)
		if type == "Point":
			self.Mass = 5
			self.Position = [0, 0, 0]
			self.Rotation = [0, 0, 0]
			self.Velocity = [0, 0, 0]
			self.Size = [2, 1, 4]
			self.Restitution = 0.7
			self.Friction = 2
			self.Anchored = False
		elif type == "Floor":
			self.Mass = 0
			self.Position = [0, 0, 0]
			self.Velocity = [0, 0, 0]
			self.Size = [2047, 0, 2047]
			self.Anchored = True
			def reset(*args):
				self.Anchored = True
			self.propertyChanged(Property.Anchored, reset)
		elif type == "Camera":
			self.Position = [0, 0, 50]
			self.Rotation = [0, 0, 0]
			self.FOV = 90
			self.Target = None  # optional Object the camera follows
			self.Offset = [0, 10, 30]  # follow offset relative to target
			self.Anchored = True  # cameras are not affected by physics
		elif type == "Player":
			self.Mass = 5
			self.Position = [0, 0, 0]
			self.Rotation = [0, 0, 0]
			self.Velocity = [0, 0, 0]
			self.Size = [2, 2, 2]
			self.Restitution = 0.0  # players don't bounce
			self.Friction = 2
			self.Anchored = False
			self.WalkSpeed = 2
			self.JumpPower = 8
			self.OnGround = False

		self.Type = type
		return self

	### CAMERA LOGIC ###

	def follow(self, target, offset=None):
		"""Make a Camera track a target object each step."""
		if self.Type != "Camera":
			raise TypeError("follow() is only valid on a Camera object")
		self.Target = target
		if offset is not None:
			self.Offset = list(offset)
		return self

	def updateCamera(self):
		"""Reposition the camera relative to its target (call once per tick)."""
		if self.Type != "Camera" or self.Target is None:
			return
		tx, ty, tz = self.Target.Position
		ox, oy, oz = self.Offset
		self.Position = [tx + ox, ty + oy, tz + oz]

	def worldToScreen(self, point, screen_w=800, screen_h=600):
		"""Project a 3D world point to 2D screen coords using this Camera.

		Returns (sx, sy, depth) or None when the point is behind the camera.
		"""
		if self.Type != "Camera":
			raise TypeError("worldToScreen() is only valid on a Camera object")
		# Translate world point into camera space.
		px = point[0] - self.Position[0]
		py = point[1] - self.Position[1]
		pz = point[2] - self.Position[2]
		# Depth toward the camera's view direction (looking down -Z).
		depth = -pz
		if depth <= MathEnum.Min:
			return None  # behind / on the camera plane
		# Perspective projection from field of view.
		from math import tan, radians
		focal = (screen_h / 2) / tan(radians(self.FOV) / 2)
		sx = (px * focal / depth) + screen_w / 2
		sy = (py * focal / depth) + screen_h / 2
		return (sx, sy, depth)

	### PLAYER LOGIC ###

	def move(self, dx=0, dz=0):
		"""Apply walk input to a Player along the X/Z plane."""
		if self.Type != "Player":
			raise TypeError("move() is only valid on a Player object")
		self.Velocity[0] = dx * self.WalkSpeed
		self.Velocity[2] = dz * self.WalkSpeed

	def jump(self):
		"""Launch a Player upward if it is currently grounded."""
		if self.Type != "Player":
			raise TypeError("jump() is only valid on a Player object")
		if self.OnGround:
			self.Velocity[1] = self.JumpPower
			self.OnGround = False

	def bindControls(self, screen=None):
		"""Bind WASD + space keyboard controls via turtle (interactive mode)."""
		if self.Type != "Player":
			raise TypeError("bindControls() is only valid on a Player object")
		screen = screen or t.Screen()
		screen.listen()
		screen.onkeypress(lambda: self.move(dz=1), "w")
		screen.onkeypress(lambda: self.move(dz=-1), "s")
		screen.onkeypress(lambda: self.move(dx=-1), "a")
		screen.onkeypress(lambda: self.move(dx=1), "d")
		screen.onkeyrelease(lambda: self.move(0, 0), "w")
		screen.onkeyrelease(lambda: self.move(0, 0), "s")
		screen.onkeyrelease(lambda: self.move(0, 0), "a")
		screen.onkeyrelease(lambda: self.move(0, 0), "d")
		screen.onkeypress(self.jump, "space")
		return self

	def step(self):
		if self.Anchored: return (None)
		gx, gy, gz = self.workspace.GravityDirection
		g = self.workspace.Gravity
		f = self.Friction
		r = self.workspace.AirResistance

		ax, ay, az = gx * g, gy * g, gz * g

		self.Velocity[0] += ax
		self.Velocity[1] += ay
		self.Velocity[2] += az

		self.Position[0] += self.Velocity[0]
		self.Position[1] += self.Velocity[1]
		self.Position[2] += self.Velocity[2]

		if self.Type in ("Point", "Player"):
			floor = self.workspace.getFloor()
			if floor:
				# Floor bounds
				floor_min_x = floor.Position[0] - floor.Size[0] / 2
				floor_max_x = floor.Position[0] + floor.Size[0] / 2
				floor_min_z = floor.Position[2] - floor.Size[2] / 2
				floor_max_z = floor.Position[2] + floor.Size[2] / 2
				floor_top_y = floor.Position[1]
	
				# Point bottom
				point_bottom = self.Position[1] - self.Size[1] / 2
	
				# Check if inside X/Z bounds
				inside_x = floor_min_x <= self.Position[0] <= floor_max_x
				inside_z = floor_min_z <= self.Position[2] <= floor_max_z
	
				# Check collision with floor
				if inside_x and inside_z and point_bottom <= floor_top_y:
					# Snap to surface
					self.Position[1] = floor_top_y + self.Size[1] / 2
	
					# Bounce
					self.Velocity[1] *= -self.Restitution
	
					# Optional friction (this part was odd before)
					friction = 1 - (f / 100)
					self.Velocity[0] *= friction
					self.Velocity[2] *= friction

					# Players track whether they're grounded (for jumping)
					if self.Type == "Player":
						self.OnGround = True
				elif self.Type == "Player":
					self.OnGround = False
		self.Velocity[1] *= 1 + (f / 100)

	def setProperty(self, property: Property, value):
		success = False

		if property == Property.Position and isinstance(value, tuple):
			self.Position = list(value)
			success = True

		elif property == Property.Velocity and isinstance(value, tuple):
			self.Velocity = list(value)
			success = True

		elif property == Property.Mass and isinstance(value, int):
			self.Mass = value
			success = True

		elif property == Property.Restitution and isinstance(value, float):
			self.Restitution = value
			success = True

		elif property == Property.Friction and isinstance(value, int):
			self.Friction = value
			success = True

		elif property == Property.Anchored and isinstance(value, bool):
			self.Anchored = value
			success = True

		elif property == Property.Size and isinstance(value, tuple):
			self.Size = value
			success = True

		if success:
			if hasattr(self, "_listeners") and property in self._listeners:
				for callback in self._listeners[property]:
					callback(value)

			return True, f"Set {property} to {value}"

		return False, None

	def getProperty(self, property: Property):
		if property == Property.Position: return True, self.Position
		elif property == Property.Velocity: return True, self.Velocity
		elif property == Property.Mass: return True, self.Mass
		elif property == Property.Restitution: return True, self.Restitution
		elif property == Property.Friction: return True, self.Friction
		elif property == Property.Anchored: return True, self.Anchored
		elif property == Property.Size: return True, self.Size
		else: return (False, None)

	def propertyChanged(self, property: Property, callback):
		if property not in self._listeners:
			self._listeners[property] = []
		self._listeners[property].append(callback)


### NETWORKING ###


class NetClient:
	"""Connects a local Player to an Open-Physics server.

	Streams the local player's state up each tick and keeps a dict of the
	other connected players' state (positions, velocities, etc.) in sync.
	Protocol: newline-delimited JSON over TCP (see server.py).
	"""

	DEFAULT_PORT = 5555

	def __init__(self, host, port, player, name=None):
		self.host = host
		self.port = port
		self.player = player
		self.name = name
		self.sock = None
		self.id = None
		self.connected = False
		self._remote = {}            # id -> player state dict (excludes self)
		self._buf = ""
		self._lock = threading.Lock()

	def connect(self):
		self.sock = socket.create_connection((self.host, self.port), timeout=5)
		self.sock.settimeout(None)
		self.connected = True
		if self.name:
			self._send({"type": "hello", "name": self.name})
		threading.Thread(target=self._recv_loop, daemon=True).start()
		return self

	def _send(self, obj):
		if not self.sock:
			return
		try:
			self.sock.sendall((json.dumps(obj) + "\n").encode())
		except OSError:
			self.connected = False

	def send_state(self):
		"""Push the local player's current physics state to the server."""
		if not self.connected:
			return
		self._send({
		 "type": "update",
		 "player": {
		  "Position": list(self.player.Position),
		  "Velocity": list(self.player.Velocity),
		  "Rotation": list(getattr(self.player, "Rotation", [0, 0, 0])),
		  "Size": list(self.player.Size),
		 },
		})

	def players(self):
		"""Return a snapshot of the other players' state, keyed by id."""
		with self._lock:
			return dict(self._remote)

	def close(self):
		self.connected = False
		if self.sock:
			try:
				self.sock.close()
			except OSError:
				pass

	def _recv_loop(self):
		while self.connected:
			try:
				data = self.sock.recv(4096)
			except OSError:
				break
			if not data:
				break
			self._buf += data.decode(errors="ignore")
			while "\n" in self._buf:
				line, self._buf = self._buf.split("\n", 1)
				line = line.strip()
				if line:
					self._handle(line)
		self.connected = False

	def _handle(self, line):
		try:
			msg = json.loads(line)
		except json.JSONDecodeError:
			return
		mtype = msg.get("type")
		if mtype == "welcome":
			self.id = msg.get("id")
		elif mtype == "state":
			players = msg.get("players", {})
			with self._lock:
				self._remote = {
				 int(pid): state
				 for pid, state in players.items()
				 if int(pid) != self.id
				}


### RENDERING ###


class Renderer:
	"""A turtle-based GUI for the engine.

	Steps the workspace every frame and draws each object by projecting its
	3D position through a Camera onto the 2D screen. The floor is drawn as a
	ground line, objects as depth-scaled squares, and a HUD shows live stats.
	"""

	# fill / outline colours per object type
	COLORS = {
	 "Point": ("#f0883e", "#ffd7a8"),
	 "Player": ("#3fb950", "#aff5b4"),
	 "Floor": ("#30363d", "#484f58"),
	}
	REMOTE_COLOR = ("#bc8cff", "#e2c5ff")

	def __init__(self, workspace, camera, net=None, player=None,
	             width=900, height=650):
		self.workspace = workspace
		self.camera = camera
		self.net = net
		self.player = player
		self.width = width
		self.height = height

		self.screen = t.Screen()
		self.screen.setup(width, height)
		self.screen.title("Open-Physics Engine")
		self.screen.bgcolor("#0d1117")
		self.screen.tracer(0)

		# one drawing pen for the world, one for the HUD text
		self._pen = t.Turtle(visible=False)
		self._pen.hideturtle()
		self._pen.speed(0)
		self._hud = t.Turtle(visible=False)
		self._hud.hideturtle()
		self._hud.speed(0)

	### projection helpers ###

	def _focal(self):
		from math import tan, radians
		return (self.height / 2) / tan(radians(self.camera.FOV) / 2)

	def _project(self, point):
		"""World point -> (turtle_x, turtle_y, depth) or None if behind cam."""
		res = self.camera.worldToScreen(point, self.width, self.height)
		if res is None:
			return None
		sx, sy, depth = res
		# turtle origin is screen centre with +y pointing up
		return (sx - self.width / 2, sy - self.height / 2, depth)

	### drawing primitives ###

	def _box(self, cx, cy, half, fill, outline):
		"""Axis-aligned filled square centred on (cx, cy)."""
		pen = self._pen
		pen.penup()
		pen.goto(cx - half, cy - half)
		pen.setheading(0)
		pen.color(outline, fill)
		pen.pensize(2)
		pen.pendown()
		pen.begin_fill()
		for _ in range(2):
			pen.forward(half * 2)
			pen.left(90)
			pen.forward(half * 2)
			pen.left(90)
		pen.end_fill()
		pen.penup()

	def _draw_object(self, position, size, colors):
		proj = self._project(position)
		if proj is None:
			return
		cx, cy, depth = proj
		half = (max(size) / 2) * self._focal() / depth
		half = max(3.0, min(half, 220.0))
		self._box(cx, cy, half, colors[0], colors[1])

	### the world ###

	def _draw_floor(self):
		floor = self.workspace.getFloor()
		if not floor:
			return
		proj = self._project([0, floor.Position[1], 0])
		if proj is None:
			return
		y = proj[1]
		pen = self._pen
		# faint fill below the ground line
		pen.penup()
		pen.goto(-self.width / 2, y)
		pen.setheading(0)
		pen.color("#161b22")
		pen.begin_fill()
		pen.pendown()
		pen.goto(self.width / 2, y)
		pen.goto(self.width / 2, -self.height / 2)
		pen.goto(-self.width / 2, -self.height / 2)
		pen.goto(-self.width / 2, y)
		pen.end_fill()
		pen.penup()
		# the ground line itself
		pen.goto(-self.width / 2, y)
		pen.color("#30363d")
		pen.pensize(3)
		pen.pendown()
		pen.goto(self.width / 2, y)
		pen.penup()

	def _draw_hud(self):
		hud = self._hud
		hud.clear()
		hud.penup()
		lines = [
		 f"tick {TICK}   t={self.workspace.getGlobalTime()}s",
		 f"objects: {len(self.workspace.getAllObjects())}",
		]
		if self.net is not None:
			status = "connected" if self.net.connected else "offline"
			lines.append(f"server: {status}  peers: {len(self.net.players())}")
		if self.player is not None:
			lines.append("move: WASD   jump: space")
		x = -self.width / 2 + 16
		y = self.height / 2 - 28
		hud.color("#58a6ff")
		hud.goto(x, y)
		hud.write("OPEN-PHYSICS ENGINE", font=("Courier", 14, "bold"))
		hud.color("#8b949e")
		for i, line in enumerate(lines, start=1):
			hud.goto(x, y - 22 * i)
			hud.write(line, font=("Courier", 11, "normal"))

	def _draw(self):
		self._pen.clear()
		self._draw_floor()
		for obj in self.workspace.getAllObjects().values():
			colors = self.COLORS.get(obj.Type, ("#c9d1d9", "#ffffff"))
			self._draw_object(obj.Position, obj.Size, colors)
		if self.net is not None:
			for state in self.net.players().values():
				self._draw_object(
				 state.get("Position", [0, 0, 0]),
				 state.get("Size", [2, 2, 2]),
				 self.REMOTE_COLOR,
				)
		self._draw_hud()

	### loop ###

	def _frame(self):
		global TICK
		stepAll()
		self.camera.updateCamera()
		if self.net is not None and self.net.connected:
			self.net.send_state()
		self._draw()
		self.screen.update()
		TICK += 1
		self.screen.ontimer(self._frame, int(1000 / FPS))

	def run(self):
		if self.player is not None:
			self.player.bindControls(self.screen)
		self._frame()
		self.screen.mainloop()


### MAIN ###


# Example
work = Workspace()
floor = Object().create("Floor")
point = Object().create("Point")
point.setProperty(Property.Restitution, 0.7)
point.setProperty(Property.Position, (-50, 50, 0))
point.setProperty(Property.Velocity, (2, 0, 0))
point.setProperty(Property.Friction, 2)
floor.setProperty(Property.Position, (0, -20, 0))
work.addObject(point)
work.addObject(floor)
work.setProperty(Property.AirResistance, 1)


# Functions / Helpers
def stepAll():
	for obj in work.getAllObjects().values():
		obj.step()


# Console fallback loop (used with --no-gui)
def console_loop(net=None):
	global TICK
	while True:
		sleep(1 / FPS)
		stepAll()

		if net and net.connected:
			net.send_state()
			remote = net.players()
			print(f"[tick {TICK}] {len(remote)} other player(s) online")
			for pid, state in remote.items():
				print(f"  {state.get('name', pid)} @ {state.get('Position')}")
		else:
			for obj in work.getAllObjects().values():
				print(obj.Position)

		TICK += 1


# Main loop
def main(server=None, name=None, gui=True):
	net = None
	player = None

	# Every scene gets a camera to project the world onto the screen.
	camera = Object().create("Camera")

	# If a server IP was supplied, spawn a local Player and connect to it.
	if server:
		host, sep, port = server.partition(":")
		port = int(port) if sep and port else NetClient.DEFAULT_PORT
		player = Object().create("Player")
		player.setProperty(Property.Position, (0, 50, 0))
		work.addObject(player)
		# Chase camera so you can see yourself move around.
		camera.follow(player, offset=(0, 10, 40))
		net = NetClient(host, port, player, name=name)
		try:
			net.connect()
			print(f"Connected to OPE server at {host}:{port} (you are player {name or 'anon'})")
		except OSError as e:
			print(f"Could not connect to {host}:{port}: {e}")
			net = None

	if gui:
		Renderer(work, camera, net=net, player=player).run()
	else:
		console_loop(net=net)


def parse_args():
	parser = argparse.ArgumentParser(description="Open-Physics engine")
	parser.add_argument("--server",
	                    help="server IP to connect to, e.g. 192.168.1.10 or 192.168.1.10:5555")
	parser.add_argument("--name", help="player name to register on the server")
	parser.add_argument("--no-gui", dest="gui", action="store_false",
	                    help="run the headless console loop instead of the window")
	parser.set_defaults(gui=True)
	return parser.parse_args()


# Start program

if not LIBRARY_MODE:
	# if running normally, showcase / connect; if imported as a library, do nothing
	_args = parse_args()
	main(server=_args.server, name=_args.name, gui=_args.gui)
