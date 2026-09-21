"""The eulib demo — run it with:  python -m eulib"""

import random

from . import cone, cube, cylinder, finalui, pyramid, sphere

SHAPES = {
    "Cube": lambda: cube(1.2),
    "Sphere": lambda: sphere(0.8),
    "Pyramid": lambda: pyramid(1.4),
    "Cylinder": lambda: cylinder(0.5, 1.3),
    "Cone": lambda: cone(0.7, 1.3),
}
COLORS = ["#4f8ef7", "#e06666", "#4fbf9f", "#f7b84f", "#9d6bf5", "#f76fb0"]


def main():
    window = finalui.run(title="eulib demo", size=(1000, 640))

    split = window.row(fill="both", expand=True, pad=0)
    panel = split.column(fill="y", expand=False, pad=0)
    view = split.view3d()

    panel.heading("eulib")
    panel.label("drag = orbit   scroll = zoom\nright-drag = pan", size=9,
                color=window.theme["subtle"])
    panel.separator()

    log = None  # made further down; used by the callbacks below

    def say(message):
        window.toast(message)
        if log:
            log.append(message)

    def spin_everything(speed):
        for mesh in view.meshes:
            view.spin(mesh, y=speed)

    def add_shape():
        mesh = SHAPES[picker.value]()
        mesh.color = random.choice(COLORS)
        mesh.move(random.uniform(-2.5, 2.5), random.uniform(0.7, 2.2),
                  random.uniform(-2.5, 2.5))
        view.add(mesh)
        view.spin(mesh, y=speed.value)
        say(f"added a {picker.value.lower()}")

    def clear_scene():
        view.clear()
        say("cleared the scene")

    def toggle_wireframe(on):
        for mesh in view.meshes:
            mesh.wireframe = on
        view.render()

    picker = panel.dropdown(list(SHAPES), width=12)
    panel.button("Add shape", on_click=add_shape)
    panel.button("Clear scene", on_click=clear_scene)
    speed = panel.slider(0, 4, value=1.0, label="spin speed",
                         on_change=spin_everything)
    panel.checkbox("wireframe", on_toggle=toggle_wireframe)
    panel.separator()

    name = panel.input(placeholder="your name")
    panel.button("Say hi", on_click=lambda: say(f"hi {name.value or 'there'}!"))
    log = panel.textbox(readonly=True, height=7, width=26, fill="both",
                        expand=True)

    # a starter scene
    view.spin(view.add_cube(1.4, color="#4f8ef7").move(y=0.7), y=1.0)
    view.spin(view.add_sphere(0.7, color="#e06666").move(x=2.4, y=0.7), y=1.0)
    view.spin(view.add_pyramid(1.4, color="#4fbf9f").move(x=-2.4, y=0.7), y=1.0)

    window.on_key("space", add_shape)
    say("welcome! press space to add shapes")


main()
