"""Tests for eulib. Run with:  python tests/test_eulib.py

The math tests always run. The GUI tests need a display — on a headless
machine use:  xvfb-run python tests/test_eulib.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PASSED = []


def check(name, fn):
    fn()
    PASSED.append(name)
    print(f"  ok - {name}")


# ---------------------------------------------------------------- math only

def test_theme_colors():
    from eulib.theme import hex_to_rgb, rgb_to_hex, shade
    assert hex_to_rgb("#4f8ef7") == (79, 142, 247)
    assert hex_to_rgb("#fff") == (255, 255, 255)
    assert rgb_to_hex(255, 0, 128) == "#ff0080"
    assert rgb_to_hex(300, -5, 12.6) == "#ff000d"
    assert shade("#808080", 0.5) == "#404040"
    assert shade("#000000", 2.0) == "#ffffff"


def test_primitives():
    from eulib import box, cone, cube, cylinder, plane, pyramid, sphere
    c = cube(2)
    assert len(c.vertices) == 8 and len(c.faces) == 6
    xs = sorted(v[0] for v in c.vertices)
    assert xs[0] == -1.0 and xs[-1] == 1.0
    b = box(2, 4, 6)
    assert max(v[1] for v in b.vertices) == 2.0
    s = sphere(1, detail=8)
    assert len(s.faces) == 8 * 16
    for v in s.vertices:  # every vertex sits on the sphere
        r = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
        assert abs(r - 1.0) < 1e-9
    for mesh in (cylinder(), cone(), pyramid(), plane()):
        assert mesh.vertices and mesh.faces
        for face in mesh.faces:
            assert all(0 <= i < len(mesh.vertices) for i in face)


def test_mesh_transforms():
    from eulib import cube
    m = cube(2)
    m.move(1, 2, 3).move(x=1)
    assert m.position == [2.0, 2.0, 3.0]
    m.move_to(0, 0, 0)
    m.rotate(y=90)
    world = m.world_vertices()
    # rotating (1,1,1) by 90 deg around y -> (1,1,-1)
    assert any(abs(x - 1) < 1e-9 and abs(y - 1) < 1e-9 and abs(z + 1) < 1e-9
               for x, y, z in world)
    m.rotate_to(0, 0, 0)
    m.resize(3)
    assert max(v[0] for v in m.world_vertices()) == 3.0
    m.resize(1, 2, 1)
    assert max(v[1] for v in m.world_vertices()) == 2.0


def test_mesh_chaining_and_custom():
    from eulib import Mesh
    m = Mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)], color="#123456")
    assert m.move(1).rotate(z=10).resize(2) is m
    assert m.color == "#123456"


# ------------------------------------------------------------------- gui

def _display_available():
    if sys.platform.startswith("win") or sys.platform == "darwin":
        return True
    return bool(os.environ.get("DISPLAY"))


def test_gui():
    import tkinter as tk

    import eulib
    from eulib import finalui

    window = finalui.run(title="test", size=(800, 500), auto=False)
    assert isinstance(window, tk.Tk)
    assert eulib.run.__func__ is finalui.run.__func__

    # one of everything
    label = window.label("hello")
    heading = window.heading("big")
    clicks = []
    button = window.button("press", on_click=lambda: clicks.append(1))
    button.click()
    assert clicks == [1]
    button.text = "renamed"
    assert button.text == "renamed"

    box = window.input(placeholder="type here", value="abc")
    assert box.value == "abc"
    box.value = "xyz"
    assert box.value == "xyz"
    box.clear()
    assert box.value == ""

    picks = []
    dd = window.dropdown(["Euler", "Verlet", "RK4"], on_select=picks.append)
    assert dd.value == "Euler"
    dd.value = "RK4"
    assert dd.value == "RK4"
    dd.options = ["a", "b"]
    assert dd.value == "a" and dd.options == ["a", "b"]

    slider = window.slider(0, 10, value=4)
    assert slider.value == 4.0
    slider.value = 7
    assert slider.value == 7.0

    cb = window.checkbox("on?", checked=True)
    assert cb.checked is True
    cb.checked = False
    assert cb.checked is False

    log = window.textbox(readonly=True)
    log.append("line 1")
    log.append("line 2")
    assert log.value == "line 1\nline 2"

    row = window.row()
    row.button("a")
    row.button("b")
    col = window.column()
    col.label("stacked")
    window.separator()
    window.spacer(4)

    label.hide()
    label.show()
    heading.disable()
    heading.enable()

    # 3d view
    view = window.view3d(width=400, height=300)
    c = view.add_cube(color="#4f8ef7")
    s = view.add_sphere(0.5, detail=6)
    view.add_pyramid()
    view.spin(c, y=2)
    window.update_idletasks()
    window.update()
    view.render()
    items = view.find_all()
    assert len(items) > 50, f"expected a drawn scene, got {len(items)} items"

    # wireframe + camera moves still render
    s.wireframe = True
    view.yaw += 30
    view.pitch = 10
    view.zoom(0.9)
    view.look_at(0, 0.5, 0)
    assert len(view.find_all()) > 50
    view.remove(s)
    view.clear()
    view.render()

    # timers
    import time
    ticks = []
    rep = window.every(10, lambda: ticks.append(1))
    deadline = time.time() + 2.0
    while not ticks and time.time() < deadline:
        window.update()
        time.sleep(0.01)
    rep.stop()
    assert ticks, "Repeater never fired"

    # toast + child window
    window.toast("hi")
    kid = window.child(title="child")
    kid.label("in the child")
    kid.close()

    window.update()
    window.close()
    print("  (gui widgets all behaved)")


def test_layout_groups():
    from eulib import Column, Row, Stack, finalui

    window = finalui(size=(900, 600))

    # vertical([...]) -> a Column holding the widgets, top to bottom
    v1, v2, v3 = window.view3d(), window.view3d(), window.view3d()
    col = window.vertical([v1, v2, v3])
    assert isinstance(col, Column)
    for v in (v1, v2, v3):
        assert v.winfo_manager() == "pack"
        assert str(v.pack_info()["in"]) == str(col)
        assert v.pack_info()["side"] == "top"

    # horizontal([...]) -> a Row, side by side, with a custom gap
    buttons = [window.button("a"), window.button("b")]
    row = window.horizontal(buttons, gap=2)
    assert isinstance(row, Row)
    for b in buttons:
        info = b.pack_info()
        assert str(info["in"]) == str(row)
        assert info["side"] == "left"
        assert int(info["padx"]) == 2

    # stack([...]) -> layered widgets; first = base, tuples pick an anchor
    base = window.view3d()
    fps = window.label("fps: 60")
    hud = window.stack([base, (fps, "nw")])
    assert isinstance(hud, Stack)
    assert hud.base is base
    assert base.winfo_manager() == "pack"
    assert fps.winfo_manager() == "place"
    info = fps.place_info()
    assert info["anchor"] == "nw"
    assert float(info["relx"]) == 0.0 and float(info["rely"]) == 0.0

    # fill=True overlays cover the whole stack
    pause = window.label("paused")
    hud.add(pause, fill=True)
    assert float(pause.place_info()["relwidth"]) == 1.0

    # widgets created *on* a stack become layers too
    st = window.stack()
    inner_base = st.view3d()
    assert st.base is inner_base
    corner = st.label("top right", anchor="ne")
    assert corner.winfo_manager() == "place"
    assert corner.place_info()["anchor"] == "ne"

    # hide/show works for placed overlays
    fps.hide()
    assert fps.winfo_manager() == ""
    fps.show()
    assert fps.winfo_manager() == "place"

    # bad anchors and cross-container moves fail with friendly errors
    try:
        st.add(window.label("x"), anchor="topleft")
        raise AssertionError("expected ValueError for bad anchor")
    except ValueError as err:
        assert "anchor" in str(err)
    other = window.column()
    stray = other.label("stray")
    try:
        window.vertical([stray])
        raise AssertionError("expected ValueError for cross-container move")
    except ValueError as err:
        assert "same window" in str(err)

    # the moved-in views actually get screen space
    window.update_idletasks()
    window.update()
    for v in (v1, v2, v3):
        assert v.winfo_height() > 10

    window.close()


def test_gui_light_theme():
    from eulib import finalui
    window = finalui(theme="light", size=(300, 200))   # classic constructor
    window.label("light mode")
    window.dropdown(["a", "b"])
    view = window.view3d(width=200, height=150)
    view.add_cube()
    window.update()
    view.render()
    assert len(view.find_all()) > 5
    window.close()


def main():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("eulib needs tkinter — install it first (e.g. apt install python3-tk)")
        sys.exit(1)

    print("math tests:")
    check("theme colors", test_theme_colors)
    check("primitives", test_primitives)
    check("mesh transforms", test_mesh_transforms)
    check("mesh chaining", test_mesh_chaining_and_custom)

    if _display_available():
        print("gui tests:")
        check("gui smoke test", test_gui)
        check("vertical/horizontal/stack", test_layout_groups)
        check("light theme", test_gui_light_theme)
    else:
        print("gui tests: skipped (no display — try xvfb-run)")

    print(f"\nall {len(PASSED)} test groups passed")


if __name__ == "__main__":
    main()
