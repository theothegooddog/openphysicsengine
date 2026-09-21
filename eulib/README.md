# eulib

A tiny, friendly UI library on top of tkinter. **finalui is the `tk.Tk()` of eulib** — one class, one line, and you have a window. No `mainloop()` to remember, no `StringVar`, no `.pack()` boilerplate.

Zero dependencies (it's all standard library — you just need tkinter, which comes with most Pythons).

**Try the demo:** `python -m eulib`

```python
from eulib import finalui

window = finalui.run(title="My App")

window.heading("Hello!")
name = window.input(placeholder="your name")
window.button("Greet", on_click=lambda: window.toast(f"hi {name.value}!"))
window.dropdown(["Cube", "Sphere", "Pyramid"], on_select=print)

view = window.view3d()          # a real 3D viewport — drag it!
cube = view.add_cube()
view.spin(cube, y=1)

# that's it — the window runs itself when the script ends
```

---

## The window

```python
window = finalui.run(title="My App", size=(900, 600), theme="dark")
```

`finalui.run()` gives you the window **immediately** so you can add widgets to it, and the event loop starts by itself once your script reaches the end. If you want control:

- `window.loop()` — start the event loop right now (blocks until the window closes)
- `finalui.run(auto=False)` — no magic; call `window.loop()` yourself
- `window = finalui(...)` — classic style, exactly like `tk.Tk()` (then call `window.loop()`)

Options: `title`, `size=(w, h)`, `theme="dark"|"light"`, `resizable=True`, `padding=14`, `background="#112233"`.

Handy window stuff:

| call | what it does |
|---|---|
| `window.toast("saved!")` | little message that pops up and fades away |
| `window.alert("msg")` | info popup |
| `window.confirm("sure?")` | yes/no popup → `True`/`False` |
| `window.prompt("name?")` | ask the user to type → `str` or `None` |
| `window.every(ms, fn)` | run `fn` repeatedly (returns a timer with `.stop()`) |
| `window.later(ms, fn)` | run `fn` once, later |
| `window.on_key("space", fn)` | call `fn()` on a key press |
| `window.on_close(fn)` | call `fn()` right before closing |
| `window.child("title")` | open an extra window (same easy API) |
| `window.fullscreen()` | go fullscreen |
| `window.close()` | close the window |
| `window.theme` | the color dict, e.g. `window.theme["accent"]` |

It's still a real `tk.Tk` underneath, so anything tkinter can do still works.

## Widgets

Every widget is one call on a window (or row / column). Each call **creates it, lays it out, and returns it**:

```python
label    = window.label("some text", size=12, bold=False, color="#9aa0ab")
heading  = window.heading("Big Title")
button   = window.button("Click me", on_click=fn)
box      = window.input(placeholder="type here", on_change=fn, on_enter=fn, password=False)
picker   = window.dropdown(["a", "b", "c"], on_select=fn)
slider   = window.slider(0, 100, value=50, step=1, label="volume", on_change=fn)
tick     = window.checkbox("enable gravity", checked=True, on_toggle=fn)
log      = window.textbox(readonly=True, height=6)      # log.append("line")
window.separator()
window.spacer(10)
```

The ones that hold something have a `.value` you can read *and* write (`box.value`, `picker.value`, `slider.value`; checkboxes also have `.checked`). Buttons and labels have `.text`. Dropdowns have `.options` you can swap out. Callbacks get the new value: `on_change(text)`, `on_select(choice)`, `on_toggle(bool)`.

Every widget also has `.hide()` / `.show()` / `.disable()` / `.enable()`.

### Layout

Widgets stack top-to-bottom by default. For anything fancier, `row()` and `column()` are containers with the exact same methods:

```python
split = window.row(fill="both", expand=True)
sidebar = split.column(fill="y", expand=False)
main    = split.column()

sidebar.button("I'm in the sidebar")
main.view3d()
```

Any widget call also accepts layout keywords when you need them: `side`, `fill`, `expand`, `anchor`, `pad` / `padx` / `pady` (same meaning as tkinter's `pack`).

## 3D views

```python
view = window.view3d()               # options: width, height, grid, axes, fov, background
```

Mouse controls are built in: **drag = orbit, scroll = zoom, right-drag (or shift-drag) = pan.**

Add shapes (each returns a `Mesh`):

```python
view.add_cube(size=1, color="#4f8ef7")
view.add_box(w, h, d)
view.add_sphere(radius=1, detail=10)
view.add_cylinder(radius=0.5, height=1)
view.add_cone(radius=0.6, height=1)
view.add_pyramid(size=1)
view.add_plane(width=4, depth=4)
view.add_mesh(vertices, faces, color="#ff8800")   # your own shape
```

Move meshes around (all chainable, angles in degrees):

```python
mesh.move(x=1)             # relative          mesh.move_to(0, 2, 0)   # absolute
mesh.rotate(y=45)          #                   mesh.rotate_to(0, 0, 0)
mesh.resize(2)             # uniform           mesh.resize(1, 3, 1)    # stretch y
mesh.color = "#e06666"     # also: .visible, .wireframe, .outline
```

Animation:

```python
view.spin(mesh, y=1)                 # rotate 1° per frame, forever
view.stop_spin(mesh)                 # or view.stop_spin() for all
view.animate(update, fps=60)         # run your own function every frame
view.stop()                          # stop everything
```

Camera: `view.yaw`, `view.pitch`, `view.distance`, `view.fov`, `view.look_at(x, y, z)`, `view.zoom(0.9)`. Scene extras: `view.show_grid`, `view.show_axes`, `view.light`, `view.ambient`. `view.remove(mesh)` / `view.clear()` to empty it, `view.render()` to force a redraw (it usually happens automatically).

It's software-rendered on a plain canvas (perspective projection, depth-sorted faces, flat shading) — no OpenGL, no installs, fast enough for a few thousand faces.

## Using the classes directly

Prefer plain tkinter style? Every widget is a normal class that works inside any tk container:

```python
import eulib
window = eulib.finalui()                      # finalui / FinalUI / Window all work
btn = eulib.Button(window._content(), text="hi", on_click=fn)
btn.pack()
mesh = eulib.sphere(2, color="#00ff88")       # Mesh, cube, box, sphere, ...
window.loop()
```

## Tests

```
python tests/test_eulib.py            # on a headless machine: xvfb-run python tests/test_eulib.py
```
