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
import ast
import time
import math
import random
import threading

from enum import Enum
from time import sleep
from math import floor, sqrt as mfloor, sqrt
from sys import version

### GLOBALS ###

FPS = 30
TICK = 0
LIBRARY_MODE = __name__!="__main__"
CONSOLE = f"Running OPENPHYSICSENGINE on python {version}\n"

### HELPERS ###

class MathEnum():
	Huge = 10**1000
	Min = 1 / (10**20)

class UnsafeSceneError(BaseException):
		pass

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
	Name = "Name"
	Type = "Type"
	Source = "Source"
	Permission = "Permission"

	@staticmethod
	def from_string(name: str):
		if not isinstance(name, str):
			raise TypeError(f"Expected str, got {type(name).__name__}")
		try:
			return Property(name)
		except ValueError:
			raise InvalidPropertyError(f"Unknown property: {name}")


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

class Any:
	pass

Something = Any

class Vector3:
	def __init__(self,x:int=0,y:int=0,z:int=0):
		self.x=x
		self.y=y
		self.z=z
		self.Magnitude = math.sqrt((x**2)+(y**2)+(z**2))
		self.Normal = (x+y+z)/x if(x>y)and(x>z)else(x+y+z)/y if(y>x)and(y>z)else(x+y+z)/z

def is_safe(code_str):
		try:
			tree = ast.parse(code_str)
		except SyntaxError:
			return False
		for node in ast.walk(tree):
			if isinstance(node, (ast.Import, ast.ImportFrom)):
				return False
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
				if node.func.id in ['eval', 'exec', 'open', 'compile', '__import__']:
					return False
		return True

def run_safe(code_str):
	try:
		tree = ast.parse(code_str)
	except SyntaxError:
		return False
	for node in ast.walk(tree):
		if isinstance(node, (ast.Import, ast.ImportFrom)):
			return False
		if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
			if node.func.id in ['eval', 'exec', 'open', 'compile', '__import__']:
				return "Unsafe"
	# Create a base globals dictionary with your custom objects
	sandbox_globals = {
    "workspace": WORKSPACE,
    "game": {"Workspace": WORKSPACE},
    "Object": Object,
    "Property": Property,
    "Vector3": Vector3,
    "random": random,
    "time": time,
    "math": math,
    "console": Console
	}
	# Run exec. Python automatically includes standard __builtins__ this way.
	exec(code_str, sandbox_globals)

		
### Objects ###

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

WORKSPACE = Workspace()
		
class BaseObject: # baseobject = any part / physical object
	def __init__(self):
		self.Mass = 0
		self.Position = [0, 0, 0]
		self.Velocity = [0, 0, 0]
		self.Name = "baseObject"
		self.Size = [0,0,0]
		self.Restitution = 0
		self.Friction = 0
		self.Anchored = False
		self.workspace = None
		self.uuid = None
		self.Type = "baseObject"
		self._listeners = {}
		self.config={"objProperties":[Property.Mass,Property.Position,Property.Velocity,Property.Name,Property.Size,Property.Restitution,Property.Friction,Property.Anchored,Property.Type]}
		 
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
		if property in self.config["objProperties"]:
			if hasattr(self, "_listeners") and property in self._listeners:
				for callback in self._listeners[property]:
					callback(value)

			return True, f"Set {property} to {value}"

		return False, None

	def getProperty(self, property: Property):
		if property in self.config["objProperties"]: return (True, eval("self."+str(property)))
		else: return (False, None)

	def propertyChanged(self, property: Property, callback):
		if property not in self.config["objProperties"]: raise InvalidPropertyError(f"'{property}' is an invalid property.")
		if property not in self._listeners:
			self._listeners[property] = []
		self._listeners[property].append(callback)

class Instance: # instance = bare minimum
	def __init__(self):
		self.uuid = None
		self.workspace = None
		self.Type = "instance"
		self.Name = "Instance"
		self._listeners = {}
		self.config={"objProperties":[Property.Type,Property.Name]}
	def step(self): pass
	def setProperty(self,prop,val): pass
	def getProperty(self,prop,val): return(False,None)
	def propertyChanged(self, property: Property, callback):
		if property not in self.config["objProperties"]: raise InvalidPropertyError(f"'{property}' is an invalid property.")
		if property not in self._listeners:
			self._listeners[property] = []
		self._listeners[property].append(callback)

class Point(BaseObject):
	def __init__(self):
		self.Mass = 5
		self.Position = [0, 0, 0]
		self.Velocity = [0, 0, 0]
		self.Name = "Point"
		self.Size = [2, 1, 4]
		self.Restitution = 0.7
		self.Friction = 2
		self.Anchored = False
		self.workspace = None
		self.uuid = None
		self.Type = "Point"
		self._listeners = {}
		self.config={"objProperties":[Property.Mass,Property.Position,Property.Velocity,Property.Name,Property.Size,Property.Restitution,Property.Friction,Property.Anchored,Property.Type]}

class Floor(BaseObject):
	def __init__(self):
		self.Mass = 0
		self.Position = [0, 0, 0]
		self.Velocity = [0, 0, 0]
		self.Name = "Floor"
		self.Size = [2047, 0, 2047]
		self.Restitution = 0.7
		self.Friction = 2
		self.Anchored = True
		self.workspace = None
		self.uuid = None
		self.Type = None
		self._listeners = {}
		self.config={"objProperties":[Property.Mass,Property.Position,Property.Velocity,Property.Name,Property.Size,Property.Restitution,Property.Friction,Property.Anchored,Property.Type]}
		def reset():
			self.Anchored = True
		self.propertyChanged(Property.Anchored, reset)

class Code(Instance):
	def is_safe(code_str):
		try:
			tree = ast.parse(code_str)
		except SyntaxError:
			return False
		for node in ast.walk(tree):
			if isinstance(node, (ast.Import, ast.ImportFrom)):
				return False
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
				if node.func.id in ['eval', 'exec', 'open', 'compile', '__import__']:
					return False
		return True
	def __init__(self):
		self.ran = False
		self.Source = ""
		self.uuid = None
		self.workspace = None
		self.Type = "Code"
		self.Name = "Code"
		self._listeners = {}
		self.config = {"objProperties":[Property.Source,Property.Type,Property.Name]}
	def step(self):
		if self.ran: return
		threading.Thread(run_safe,(self.Source)).start()
	def run(self):
		self.step()
	def setCode(self,code:str):
		if self.is_safe(code):
			self.Source = code
			return True
		return False
	def rerun():
		self.ran = False
		self.step()

class Object:
	def create(type: ObjectType):
		type = str(type)
		match type:
			case "Point":
				return Point()
			case "Floor":
				return Floor()
			case "Code":
				return Code()

class Console:
	def log(string):
		CONSOLE += "l"+string + "/n"
	def error(string):
		CONSOLE += "e"+string + "/n"
	def warn(string):
		CONSOLE += "w"+string + "/n"
	def run(string):
		CONSOLE += run_safe(string) + "/n"
	def get()->str:
		return CONSOLE

### MAIN ###

if not is_safe(open("game.py","r").read()): raise UnsafeSceneError("Scene named '"+open("game.py","r").readlines()[0][2:].replace("\n", "")+"' is unsafe.")
run_safe(open("game.py","r").read())

# Functions / Helpers
def stepAll():
	for obj in WORKSPACE.getAllObjects().values():
		obj.step()

# Main loop
def main():
	global TICK
	while True:
		sleep(1 / FPS)
		stepAll()
		for obj in WORKSPACE.getAllObjects().values():
			print(obj.Position)
		TICK += 1

# Start program

if not LIBRARY_MODE: main()  # if running normally, showcase, otherwise, if library, do not run extra code