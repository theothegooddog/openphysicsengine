#from gamepadSupport import gamepad_support
print("initalizing engine...")
#print("Importing OpenGL Modules...")

import io
import sys
import threading
recursionLimit = 999999999
sys.setrecursionlimit(recursionLimit)

#from OpenGL.GL import *
#from OpenGL.GLU import *

#print("Imported OpenGL Modules!")
print("initalized engine!")

print("App Or Game Is Running " \
      + "Using The Bananakitssu's 3D Python Engine (BTPE) and " \
      + "it's running on version 1.0.0 BETA mode")

global walkSpeed
global version
global isTurtleRegistered
global turtle
global timerOn
global drawing
global elapsed_time
global revered
global wireframeColor
global wireframeThickness
global points
global meshesShown
global meshes
global registered_meshes
global FOV
global added_shaders
global applied_shaders
global cache
global fps
global fake_fps
import time
fps = 0
fake_fps = 0
meshesShown = 0
points = 0
wireframeThickness = 3
wireframeColor = 'green'
walkSpeed = 0.10
isTurtleRegistered = False
turtle = "N/A"
version = "1.0.0 BETA"
drawing = False
registeredAfterDraw = False
isConfigured = False
hasCamera = False
revered = True
cameras = {"dookie": "Camera"}
cache_files = []
# cache = io.FileIO(file='BTDPE_Cache')
import os

# Specify the folder path
folder_path = "BTDPE_Cache"

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Check if it's a file (not a directory)
    if os.path.isfile(file_path):
        try:
            # Open and read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                cache_files.append({'file-path': f'{folder_path}/{filename}', 'name': filename, 'folder-path': folder_path, 'cache': file.read()})
                print(f"Contents of {filename}:\n{data}\n")
        except Exception as e:
            print(f"Could not read {filename}: {e}")

print(cache_files)

def count_fps ():
    global fake_fps
    while True:
        fake_fps = fake_fps + 1
        time.sleep(0.000001)

def fps_set ():
    global fake_fps
    global fps
    while True:
        time.sleep(1)
        fps = fake_fps
        fake_fps = 0

fps_thread1 = threading.Thread(target=count_fps)
fps_thread2 = threading.Thread(target=fps_set)
fps_thread1.start()
fps_thread2.start()

cameraData = {"dookie": {"for": "dookie", "x": 0, "y": 0, "z": 0}}
meshes = { \
        "cube": {"name": "cube", "type": "cube", "shaders_enabled": False, "edges": { \
            "2": {"x": 0.001, "y": 0.001, "z": 0.001}, "3":{"x": 0.001, "y": -0.001, "z": 0.001}, \
            "6": {"x": 0.001, "y": -0.001, "z": -0.001}, "4": {"x": -0.001, "y": -0.001, "z": 0.001}, \
            "7": {"x": 0.001, "y": 0.001, "z": -0.001}, "8": {"x": -0.001, "y": 0.001, "z": -0.001}, \
            "5": {"x": -0.001, "y": -0.001, "z": -0.001}, "1": {"x": -0.001, "y": 0.001, "z": 0.001}}, \
         "mesh_position": {"x": 0, "y": 0, "z": 0}, "mesh_rotation": {"x": 0, "y": 0, "z": 0}, \
         "mesh_size": {"x": 1, "y": 1, "z": 1}, "textures": {"front": "", "back": "", "left": "", "right": "", "top": "", "bottom": ""}, \
         "mesh_color_r": 100, "mesh_color_g": 0, "mesh_color_b": 0, "mesh_attributes": {\
             "canTransparent": False, "visible": True, "opacity": 1}}, \
        "cube (1)": {"name": "cube (1)", "type": "cube", "shaders_enabled": False, "edges": { \
            "2": {"x": 0.001, "y": 0.001, "z": 0.001}, "3":{"x": 0.001, "y": -0.001, "z": 0.001}, \
            "6": {"x": 0.001, "y": -0.001, "z": -0.001}, "4": {"x": -0.001, "y": -0.001, "z": 0.001}, \
            "7": {"x": 0.001, "y": 0.001, "z": -0.001}, "8": {"x": -0.001, "y": 0.001, "z": -0.001}, \
            "5": {"x": -0.001, "y": -0.001, "z": -0.001}, "1": {"x": -0.001, "y": 0.001, "z": 0.001}}, \
         "mesh_position": {"x": 0, "y": -2, "z": 0}, "mesh_rotation": {"x": 0, "y": 0, "z": 0}, \
         "mesh_size": {"x": 1, "y": 1, "z": 1}, "textures": {"front": "", "back": "", "left": "", "right": "", "top": "", "bottom": ""}, \
         "mesh_color_r": 100, "mesh_color_g": 0, "mesh_color_b": 0, "mesh_attributes": {\
             "canTransparent": False, "visible": True, "opacity": 1}} \
    }
added_shaders = [{"name": "defualt", "data": "define main(): return 0"}]
applied_shaders = ["defualt"]

registered_meshes = ["cube", "cube (1)"]
FOV = 70
global CamX
CamX = 0
global CamY
CamY = 0
global CamZ
CamZ = 1
global CamRotZ
global CamRotY
global CamRotX
CamRotX = 0
CamRotY = 0
CamRotZ = 0

def w ():
    global CamZ
    global walkSpeed
    CamZ -= walkSpeed

def s ():
    global CamZ
    global walkSpeed
    CamZ += walkSpeed

def a ():
    global CamX
    global walkSpeed
    CamX -= walkSpeed

def d ():
    global CamX
    global walkSpeed
    CamX += walkSpeed

def up ():
    global CamY
    global walkSpeed
    CamY += walkSpeed

def down ():
    global CamY
    global walkSpeed
    CamY -= walkSpeed

def set_resolution (width=900, height=500, BTDPE_Turtle=None):
    """Sets the width and height of the turtle window."""
    BTDPE_Turtle.setup(width, height)

def get_vsync_value ():
    import pygame
    pygame.init()
    info = pygame.display.Info()
    vsync = info.current_h
    pygame.quit()
    return vsync

def left_arrow ():
    global CamRotY
    CamRotY += 0.05
    if CamRotY > 1 or CamRotY == 1:
        CamRotY = 0
    elif CamRotY < 0.00:
        CamRotY = 0.99

def right_arrow ():
    global CamRotY
    CamRotY -= 0.05
    if CamRotY > 1 or CamRotY == 1:
        CamRotY = 0
    elif CamRotY < 0.00:
        CamRotY = 0.99

def up_arrow ():
    global CamRotX
    CamRotX += 0.05
    print('did:rot')
    if CamRotX > 1 or CamRotX == 1:
        CamRotX = 0
    elif CamRotX < 0.00:
        CamRotX = 0.99

def down_arrow ():
    global CamRotX
    CamRotX -= 0.05
    if CamRotX > 1 or CamRotX == 1:
        CamRotX = 0
    elif CamRotX < 0.00:
        CamRotX = 0.99

#class Scene ():
#    def add_mesh ():
#        print('meshii')

def create_mesh (meshType, name, position, size, orientation, shadersAllowed, allShaders, shaderType, castShadows, receiveShadows, textureClass, \
                 color, attributes, textures):
    """Creates A Mesh And Adds It To The Scene."""
    if meshType == "cube":
        if position and size and orientation:
            meshes[name] = {"name": name, "type": meshType, "shadersEnabled": shadersAllowed, "mesh_position": {"x": position["x"], "y": position["y"], "z": position["z"]}, \
                          "edges": { \
            "2": {"x": 0.001, "y": 0.001, "z": 0.001}, "3":{"x": 0.001, "y": -0.001, "z": 0.001}, \
            "6": {"x": 0.001, "y": -0.001, "z": -0.001}, "4": {"x": -0.001, "y": -0.001, "z": 0.001}, \
            "7": {"x": 0.001, "y": 0.001, "z": -0.001}, "8": {"x": -0.001, "y": 0.001, "z": -0.001}, \
            "5": {"x": -0.001, "y": -0.001, "z": -0.001}, "1": {"x": -0.001, "y": 0.001, "z": 0.001}}, \
                          "mesh_rotation": orientation, "mesh_size": size, "textures": textures, "mesh_color_r": color["r"], "mesh_color_g": color["g"], \
                          "mesh_color_b": color["b"], "mesh_attributes": attributes}
            registered_meshes[len(registered_meshes)] = (name)
                          

def get_file_data (file_path):
    return None

def apply_shader (name):
    """Applies A Shader For The Engine"""
    for counter in range (0, len(applied_shaders)):
        shader = applied_shaders[counter]
        if shader:
            if shader['name'] == name:
                print('applied shader!')

def create_shader (name, data):
    """Creates A Shader For The Engine"""
    global added_shaders
    if name and data:
        added_shaders.append({"name": name, "data": data})
        return {"worked?": True, "msg": None}
    else:
        givenName = False
        givenData = False
        if name:
            givenName = True
        else:
            givenName = False
        if data:
            givenData = True
        else:
            givenData = False
        if not givenName and givenData:
            return {"worked?": False, "msg": "No Given Data And No Given Name."}
        elif not givenName:
            return {"worked?": False, "msg": "No Given Name."}
        else:
            return {"worked?": False, "msg": "No Given Data."}

def get_point_position (pointNumber, mesh):
    """Gets The Mesh's Real Point Position."""
    global CamRotX
    global CamRotY
    global CamRotZ
    if pointNumber == 1:
        point = mesh["edges"]["1"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 2:
        point = mesh["edges"]["2"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 3:
        point = mesh["edges"]["3"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 4:
        point = mesh["edges"]["4"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 5:
        point = mesh["edges"]["5"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 6:
        point = mesh["edges"]["6"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 7:
        point = mesh["edges"]["7"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}
    elif pointNumber == 8:
        point = mesh["edges"]["8"]
        x = mesh["mesh_position"]["x"] + point["x"]
        y = mesh["mesh_position"]["y"] + point["y"]
        z = mesh["mesh_position"]["z"] + point["z"]
        if point["x"] > 0.000:
            y -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] > 0.000:
                x += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        else:
            y += mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
            if point["y"] < 0.000:
                x -= mesh["mesh_rotation"]["z"] * 2 - (CamRotZ * 2)
        if point["z"] > 0.000:
            x -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        else:
            y += mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["y"] * 2 - (CamRotY * 2)
        if point["z"] > 0.000:
            y -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] > 0.000:
                z += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        else:
            y += mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
            if point["y"] < 0.000:
                z -= mesh["mesh_rotation"]["x"] * 2 - (CamRotX * 2)
        if point['x'] > 0.000:
            x += mesh['mesh_size']['x'] / 2
        else:
            x -= mesh['mesh_size']['x'] / 2
        if point['y'] > 0.000:
            y += mesh['mesh_size']['y'] / 2
        else:
            y -= mesh['mesh_size']['y'] / 2
        if point['z'] > 0.000:
            z += mesh['mesh_size']['z'] / 2
        else:
            z -= mesh['mesh_size']['z'] / 2
        return {"x": x, "y": y, "z": z}

def get_mesh_by_name (meshName):
    if meshes[meshName]:
        return meshes[meshName]
    else:
        return "nil"

def get_mesh_by_position (x, y, z):
    counted = 0
    for counter in range(0, len(registered_meshes)):
        counted += 1
        meshName = registered_meshes[counter]
        if meshes[meshName] and meshes[meshName]["mesh_position"]["x"] == x and meshes[meshName]["mesh_position"]["y"] == y and meshes[meshName]["mesh_position"]["z"] == z:
            return meshes[meshName]
    return "nil"

#GPSupport = gamepad_support()

def is_touching_obj (obj):
    """Returns the obj that it is touching"""

def draw (t):
    global wireframeColor
    global wireframeThickness
    global revered
    global CamX
    global CamY
    global CamZ
    global points
    global meshesShown
    meshesShown = 0
    points = 0
    #t.getscreen().tracer(3000)
    t.getscreen().tracer(18000)
    t.clear()
    t.penup()
    counted = 0
    for counter in range(0, len(registered_meshes)):
        counted += 1
        meshName = registered_meshes[counter]
        if meshes[meshName]:
            #t.showturtle()
            t.hideturtle()
            t.width(wireframeThickness)
            mesh = meshes[meshName]
            #print(mesh)
            if mesh['type'] == "cube":
                t.color(wireframeColor)
                point1 = get_point_position(1, get_mesh_by_name(mesh["name"]))
                point2 = get_point_position(2, get_mesh_by_name(mesh["name"]))
                point3 = get_point_position(3, get_mesh_by_name(mesh["name"]))
                point4 = get_point_position(4, get_mesh_by_name(mesh["name"]))
                point5 = get_point_position(5, get_mesh_by_name(mesh["name"]))
                point6 = get_point_position(6, get_mesh_by_name(mesh["name"]))
                point7 = get_point_position(7, get_mesh_by_name(mesh["name"]))
                point8 = get_point_position(8, get_mesh_by_name(mesh["name"]))
                #t.tracer(100)
                #if CamX - (mesh['mesh_position']['z'] + mesh['mesh_size']['z'] - 0.45) > 0:
                if (FOV) * ((point1['x'] + (CamX)) / (point1['z'] + (CamZ))) > -450 and (FOV) * ((point1['y'] + (CamY)) / (point1['z'] + (CamZ))) > -250:
                    points += len(mesh['edges'])
                    meshesShown += 1
                    t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                    #t.begin_fill()
                    t.pendown()
                    t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                    t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                    t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                    t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                    t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                    t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                    t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                    t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                    t.penup()
                    t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                    t.pendown()
                    t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                    t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                    t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                    t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                    t.penup()
                    t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                    t.pendown()
                    t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                    t.penup()
                    #t.end_fill()
                    fill = 'red'
                    fill2 = 'red'
                    fill3 = 'red'
                    if CamY > mesh['mesh_position']['y']:
                        t.fillcolor(fill)
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                    else:
                        t.fillcolor(fill)
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.end_fill()
                    if CamX > mesh['mesh_position']['x']:
                        t.fillcolor(fill2)
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.end_fill()
                    else:
                        t.fillcolor(fill2)
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                    if CamZ > mesh['mesh_position']['z']:
                        t.fillcolor(fill3)
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.end_fill()
                    else:
                        t.fillcolor(fill3)
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point6['x'] - (CamX)) / (point6['z'] + (CamZ))), (FOV) * ((point6['y'] - (CamY)) / (point6['z'] + (CamZ))))
                        t.goto((FOV) * ((point7['x'] - (CamX)) / (point7['z'] + (CamZ))), (FOV) * ((point7['y'] - (CamY)) / (point7['z'] + (CamZ))))
                        t.goto((FOV) * ((point8['x'] - (CamX)) / (point8['z'] + (CamZ))), (FOV) * ((point8['y'] - (CamY)) / (point8['z'] + (CamZ))))
                        t.goto((FOV) * ((point5['x'] - (CamX)) / (point5['z'] + (CamZ))), (FOV) * ((point5['y'] - (CamY)) / (point5['z'] + (CamZ))))
                        t.end_fill()
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.begin_fill()
                        t.goto((FOV) * ((point2['x'] - (CamX)) / (point2['z'] + (CamZ))), (FOV) * ((point2['y'] - (CamY)) / (point2['z'] + (CamZ))))
                        t.goto((FOV) * ((point3['x'] - (CamX)) / (point3['z'] + (CamZ))), (FOV) * ((point3['y'] - (CamY)) / (point3['z'] + (CamZ))))
                        t.goto((FOV) * ((point4['x'] - (CamX)) / (point4['z'] + (CamZ))), (FOV) * ((point4['y'] - (CamY)) / (point4['z'] + (CamZ))))
                        t.goto((FOV) * ((point1['x'] - (CamX)) / (point1['z'] + (CamZ))), (FOV) * ((point1['y'] - (CamY)) / (point1['z'] + (CamZ))))
                        t.end_fill()
                    #t.getscreen().tracer(100)
                    #t.forward(500)
                #CamZ -= 0.01
            """if revered == True and CamX < 5:
                CamX += 0.1
                if CamX == 5 or CamX > 5:
                    revered = False
            else:
                CamX -= 0.1
                if CamX == -5 or CamX < -4.9:
                    revered = True"""
            # 5 x 7 y
            #gamepad_x = GPSupport.read_joystick_info_input()['x']
            #gamepad_y = GPSupport.read_joystick_info_input()['y']

            #if gamepad_x > 0.25 * 100:
                #CamZ -= 0.01
            #elif gamepad_x < -0.25 - 0.01 * 100:
                #CamZ += 0.01

            #if gamepad_y > 0.25 * 100:
                #CamX -= 0.01
            #elif gamepad_y < -0.25 - 0.01 * 100:
                #CamX += 0.01
            
            #draw(t)
global timerOn
global elapsed_time

timerOn = False
elapsed_time = 0

global limit_fps

limit_fps = 60

import asyncio

async def wait_example(time_sec):
    print("Waiting asynchronously...")
    await asyncio.sleep(time_sec)
    print("Done!")

def add_draw_time ():
    import time
    global elapsed_time
    global timerOn
    if timerOn:
        elapsed_time += 1
        time.sleep(0.001)
        add_draw_time()

def stop_draw_timer ():
    global timerOn
    if timerOn:
        timerOn = False

def start_draw_timer ():
    global timerOn
    global elapsed_time
    if timerOn:
        stop_draw_timer()
    timerOn = True
    elapsed_time = 0
    add_draw_time()

global frameFunctions
frameFunctions = []

def afterFrame ():
    global frameFunctions
    for counter in range(0, len(frameFunctions)):
        function = frameFunctions[counter]
        function()

def addAfterFrame (func):
    global frameFunctions
    frameFunctions.append(func)

def request_draw_3D (t):
    #t.onkey(w, 'w')
    #t.listen()
    global drawing
    global points
    global meshesShown
    global CamX
    global CamY
    global CamZ
    global fps
    if drawing:
        return
    #start_draw_timer()
    threading.Thread(target=start_draw_timer).start()
    registeredAfterDraw = False
    drawing = True
    #t.onkeypress(w, 'w')
    #t.listen()
    draw(t)
    t.color('white')
    #t.goto(-435, -240)
    #t.write(f"FPS: {round(60 / ((elapsed_time / 1000) + 1))} / {round(60 / 1)}", False, 'left', font=('Fredoka One', 10, 'normal'))
    t.goto(-435, 240 - 10)
    t.write(f"Points From Meshes Shown: {points}", False, 'left', font=('Fredoka One', 10, 'normal'))
    t.goto(-435, 240 - 25)
    t.write(f"Meshes Shown: {meshesShown}", False, 'left', font=('Fredoka One', 10, 'normal'))
    t.goto(-435, 240 - 40)
    t.write(f"X: {round(CamX)}, Y: {round(CamY)}, Z: {round(CamZ)}", False, 'left', font=('Fredoka One', 10, 'normal'))
    drawing = False
    stop_draw_timer()
    t.goto(-435, -240)
    #t.write(f"FPS: {round(limit_fps / ((elapsed_time / 1000) + 1))} / {round(limit_fps / 1)}", False, 'left', font=('Fredoka One', 10, 'normal'))
    t.write(f"FPS: {fps} / {round(limit_fps / 1)}", False, 'left', font=('Fredoka One', 10, 'normal'))
    #print(f'Requested and ended in {elapsed_time}ms. FPS: {fps}')
    #request_draw_3D(t)
    afterFrame()

def catch_cache (t):
    return
    """t.getscreen().tracer(3000)
    t.penup()
    t.hideturtle()
    t.color('gray')
    t.goto(-(190 / 2), 100 / 2)
    t.begin_fill()
    t.forward(190)
    t.right(90)
    t.forward(100)
    t.right(90)
    t.forward(190)
    t.right(90)
    t.forward(100)
    t.end_fill()
    while True:
        t.color('gray')"""

def open_starter_screen (t):
    t.getscreen().tracer(3000)
    t.penup()
    t.hideturtle()
    t.color('gray')
    t.goto(0 - (900 / 2), 0 - (700 / 2))
    t.begin_fill()
    t.forward(900)
    t.right(90)
    t.forward(700)
    t.right(90)
    t.forward(900)
    t.right(90)
    t.forward(700)
    t.end_fill()
    ms = 0
    

def main (t):
    request_draw_3D(t)
    main(t)

# get_mesh_by_name("cube")

#print(get_point_position("1", get_mesh_by_position(0, 0, -5)))
#print(get_point_position("1", get_mesh_by_name("cube")))

def createLine (x1, y1, x2, y2, color, thickness):
    turtle.pensize(1)
    turtle.color(color)
    turtle.goto(x1, y1)
    turtle.pendown()
    turtle.goto(x2, y2)
    turtle.penup()    

def register_turtle (given_turtle):
    print("Initalizing Turtle...")
    global turtle
    global isTurtleRegistered
    if isTurtleRegistered == True:
        print("Couldn't Initalize The Turtle. It Is Already Initalized.")
        return
    else:
        turtle = given_turtle.Turtle()
        #turtle.onkey(w, 'w')
        #turtle.onkey(w, 's')
        #turtle.onkey(w, 'a')
        #turtle.onkey(w, 'd')
        #turtle.listen()
        #startListening(turtle)
        isTurtleRegistered = True
        print("Initalized Turtle.")
        #catch_cache(turtle)
        open_starter_screen(turtle)
        main(turtle)
        #request_draw_3D(turtle)
        #mainThread = threading.Thread(target=main, args=([turtle]))
        #mainThread.start()
        #main(turtle)

def OnAfterDrawing (define):
    if drawing == False and registeredAfterDraw == False:
        registeredAfterDraw = True
        define()

def createCamera (x, y, z, name, FOV):
    hasCamera = True
    cameras[name] = {"Camera"}
    cameraData[name] = {"for": name, "x": x, "y": y, "z": z, "fov": FOV}

def create3D (x, y, z, angle):
    if hasCamera == True and isConfigured == False and turtle != "N/A" and isTurtleRegistered == True:
        print('Creating 3D')
        print('Created 3D')

import turtle

if __name__ == "__main__":
    turtle.bgcolor('black')
    register_turtle(turtle)
    
"""import turtle
import math

# Initialize Turtle screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("3D Game Simulation")
screen.tracer(0)

# Create a turtle for drawing
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.color("white")

# Define 3D points for a cube
cube_points = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face
]

# Define edges connecting the points
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
    (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
]

# Perspective projection function
def project(point, fov, viewer_distance):
    factor = fov / (viewer_distance + point[2])
    x = point[0] * factor
    y = point[1] * factor
    return x, y

# Draw the cube
def draw_cube(points):
    pen.clear()
    for edge in edges:
        start = points[edge[0]]
        end = points[edge[1]]
        pen.penup()
        pen.goto(start[0], start[1])
        pen.pendown()
        pen.goto(end[0], end[1])

# Main loop
def main():
    angle = 0
    fov = 200
    viewer_distance = 4

    while True:
        # Rotate cube around Y-axis
        rotated_points = []
        for x, y, z in cube_points:
            temp_x = x * math.cos(angle) - z * math.sin(angle)
            temp_z = x * math.sin(angle) + z * math.cos(angle)
            rotated_points.append([temp_x, y, temp_z])

        # Project 3D points to 2D
        projected_points = [project(p, fov, viewer_distance) for p in rotated_points]

        # Scale and translate points for Turtle
        screen_points = [(x * 100, y * 100) for x, y in projected_points]

        # Draw the cube
        draw_cube(screen_points)

        # Update screen
        screen.update()

        # Increment rotation angle
        angle += 0.01

# Run the game loop
main()"""
