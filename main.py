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
import BTDPE
import threading

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
		self.Type = type
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

		if self.Type == "Point":
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


# Main loop
def main():
    global TICK
    BTDPE_Rendering_Thread = threading.Thread(
        target=BTDPE.register_turtle,
        args=( t, ),
        daemon=True
    )
    BTDPE.meshes = { }
    BTDPE.registered_meshes = { }
    BTDPE.create_mesh(
        "cube",
        floor.uuid,
        {"x": floor.Position[0], "y": floor.Position[1], "z": floor.Position[2]},
        {"x": floor.Size[0], "y": floor.Size[1], "z": floor.Size[2]},
        {"x": 0, "y": 0, "z": 0},
        False,
        [],
        "",
        False,
        False,
        [],
        {"r": 0, "g": 0, "b": 0},
        {"canTransparent": False, "visible": True, "opacity": 1},
        []
    )
    BTDPE.CamY = 5
    BTDPE.CamZ = 3
    BTDPE.CamX = 0
    BTDPE_Rendering_Thread.start()
    while True:
        sleep(1 / FPS)
        stepAll()
        for obj in work.getAllObjects().values():
            print(obj.Position)
            objBTDPE = next((item for item in BTDPE.meshes.values() if item is not None and isinstance(item, dict) and item.get('name') == obj.uuid), None)
            if objBTDPE is None:
                BTDPE.create_mesh(
                    "cube",
                    obj.uuid,
                    {"x": obj.Position[0], "y": obj.Position[1], "z": obj.Position[2]},
                    {"x": obj.Size[0], "y": obj.Size[1], "z": obj.Size[2]},
                    {"x": 0, "y": 0, "z": 0},
                    False,
                    [],
                    "",
                    False,
                    False,
                    [],
                    {"r": 0, "g": 0, "b": 0},
                    {"canTransparent": False, "visible": True, "opacity": 1},
                    []
                )
            else:
                objBTDPE["mesh_position"]["x"] = obj.Position[0]
                objBTDPE["mesh_position"]["y"] = obj.Position[1]
                objBTDPE["mesh_position"]["z"] = obj.Position[2]
        TICK += 1

# Start program

if not LIBRARY_MODE: main()  # if running normally, showcase, otherwise, if library, do not run extra code
