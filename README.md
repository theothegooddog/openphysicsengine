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

Version: 1.5.2b
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
- Air resistance
- Coding
- Storage
- Assets
- Scene safety
<br>
Requirements: `pip install math time enum threading random ast`
<br>
Upcoming features:
- Meshes
- Online services
- Sound
- Flexible parents
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

# ~~1.5.0b~~ [removed]

- ~~it has an actual GUI now!!~~
-~~`main.py` renders the world in a turtle window (floor, objects, players, live HUD)~~
- ~~camera projects the 3D scene to 2D; chase-cam follows your player in multiplayer~~
- ~~added `launcher.py` — a little window to pick Single Player / Multiplayer / Host Server and launch~~
- ~~`python main.py --no-gui` keeps the old console loop~~

~~How to run:~~
- ~~`python launcher.py` — start from the GUI launcher~~
- ~~`python main.py` — single-player showcase window~~
- ~~`python main.py --server 127.0.0.1:5555 --name you` — join a server~~
- ~~`python server.py` — host a multiplayer server~~

1.5.1b

- updated the api for scenes

# 1.5.2b

- WE ADDED CODING!
- also made a seperate api change so you can publish game files and run them (check game.~~osc~~py)

1.5.3b

- added threading for `code` objects so `while True:` doesnt freeze the game
- changed game extension to py for code syntax highlighting
- added console
- added full sandboxing and alot of libraries
- added checking for viruses (check virus.py)

# 1.5.4b

- added documentation, assetservice, and serverstorage
- added cloning _(idk why i didnt add that earlier)_
- baseobject inherits instance