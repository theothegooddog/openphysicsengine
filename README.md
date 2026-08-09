# OpenPhysicsEngine
### An open source physics engine.

---

[OpenPhysicsEngine](https://github.com/theothegooddog/openphysicsengine) is an open-source physics engine that you can use or branch off of for free! It is still in _beta_, but after enough updates, it should be pretty good!

###### update: its no longer in beta!
###### unupdate: its actually still in beta

---

Identifiers:
- if it is big text then big update

---

Version: 1.4.2
<br>
Current features:
- Collisions
- Objects (adding & getting)
- Floors
- Position
- Velocites
- Time (ticks & seconds)
- Gravity
- Gravity **_direction_**
<br>
Requirements: `pip install math time turtle enum`
<br>
Updates:

1.2.5a

- uploaded to github

1.2.6a

- added setProperty

1.2.7a

- created readme

1.2.8a

- added getProperty + changed main loop

1.3.0a

- added collisions, floors, restitution, and miscellaneous changes
- also i changed readme to have a/b for alpha/beta

1.3.1a

- added friction + edited main loop pt. 2

1.3.2a

- various changes tbh idk what i added

1.3.3a

- 33
- also added anchored property

# 1.4.1b

- big update!
- changed floor collisions to actually care about size
- added size
- fixed `Property.from_string()`
- only runs showcase if not in library mode
- fixed anchored

1.4.2b
- added turtle (renderer note: turtle is aliased to `t`)

# 1.5.0b

- it has an actual GUI now!!
- `main.py` renders the world in a turtle window (floor, objects, players, live HUD)
- camera projects the 3D scene to 2D; chase-cam follows your player in multiplayer
- added `launcher.py` — a little window to pick Single Player / Multiplayer / Host Server and launch
- `python main.py --no-gui` keeps the old console loop

How to run:
- `python launcher.py` — start from the GUI launcher
- `python main.py` — single-player showcase window
- `python main.py --server 127.0.0.1:5555 --name you` — join a server
- `python server.py` — host a multiplayer server

###### sorry banana i just cant really use btdpe and im going through alot of iterations

1.5.1b

- updated the api for scenes