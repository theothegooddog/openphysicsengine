"""
eulib — a tiny, friendly UI library on top of tkinter.

finalui is the tk.Tk() of eulib: one class, one line, and you have a window.

    from eulib import finalui

    window = finalui.run(title="My App")

    window.heading("Hello!")
    name = window.input(placeholder="your name")
    window.button("Greet", on_click=lambda: window.toast(f"hi {name.value}!"))
    window.dropdown(["Cube", "Sphere", "Pyramid"], on_select=print)

    view = window.view3d()          # a real 3D viewport (drag to orbit!)
    cube = view.add_cube()
    view.spin(cube, y=1)

    # group widgets SwiftUI-style: vertical / horizontal / stack
    window.horizontal([window.view3d(), window.view3d()])
    window.stack([view, (window.label("HUD"), "nw")])   # overlay in one place

    # no mainloop() needed — the window runs itself when the script ends

Run `python -m eulib` for a full demo. Docs: eulib/README.md
"""

__version__ = "1.1.0"

from .theme import THEMES
from .view3d import Mesh, View3D, box, cone, cube, cylinder, plane, pyramid, sphere
from .widgets import (Button, Checkbox, Column, Dropdown, Input, Label, Row,
                      Slider, Stack, TextBox)
from .window import ChildWindow, Repeater, finalui

# aliases, so every style works
FinalUI = finalui
Window = finalui
run = finalui.run

__all__ = [
    "finalui", "FinalUI", "Window", "run", "ChildWindow", "Repeater",
    "Label", "Button", "Input", "Dropdown", "Slider", "Checkbox", "TextBox",
    "Row", "Column", "Stack",
    "View3D", "Mesh", "cube", "box", "sphere", "cylinder", "cone", "pyramid",
    "plane",
    "THEMES", "__version__",
]
