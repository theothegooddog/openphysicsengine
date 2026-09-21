"""
3D for eulib — a software-rendered 3D view that lives in a plain tk.Canvas.

    view = window.view3d()
    cube = view.add_cube(color="#4f8ef7")
    view.spin(cube, y=1)        # spins forever
    # drag = orbit, scroll = zoom, right-drag (or shift-drag) = pan

No OpenGL, no dependencies: meshes are projected with a perspective camera,
faces are depth-sorted (painter's algorithm) and flat-shaded.
"""

import math
import tkinter as tk

from .base import EasyWidget
from .theme import get_theme, shade


# ------------------------------------------------------------------ meshes

class Mesh:
    """A 3D object: a list of vertices and the faces connecting them.

    You normally get one from view.add_cube() / eulib.sphere() etc., then
    move it around with .move() / .rotate() / .resize().
    """

    def __init__(self, vertices, faces, color="#4f8ef7", name="mesh"):
        self.vertices = [tuple(float(c) for c in v) for v in vertices]
        self.faces = [tuple(f) for f in faces]
        self.color = color
        self.name = name
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]   # degrees around x, y, z
        self.scale = [1.0, 1.0, 1.0]
        self.visible = True
        self.wireframe = False
        self.outline = None               # None = auto, False = no edges, or a color

    # --- movement (all return self so you can chain) ---

    def move(self, x=0.0, y=0.0, z=0.0):
        """Move by an amount (relative)."""
        self.position[0] += x
        self.position[1] += y
        self.position[2] += z
        return self

    def move_to(self, x=None, y=None, z=None):
        """Move to an exact spot (leave an axis out to keep it)."""
        if x is not None: self.position[0] = float(x)
        if y is not None: self.position[1] = float(y)
        if z is not None: self.position[2] = float(z)
        return self

    def rotate(self, x=0.0, y=0.0, z=0.0):
        """Rotate by degrees (relative)."""
        self.rotation[0] += x
        self.rotation[1] += y
        self.rotation[2] += z
        return self

    def rotate_to(self, x=None, y=None, z=None):
        if x is not None: self.rotation[0] = float(x)
        if y is not None: self.rotation[1] = float(y)
        if z is not None: self.rotation[2] = float(z)
        return self

    def resize(self, x=None, y=None, z=None):
        """resize(2) doubles the size; resize(1, 3, 1) stretches y only."""
        if x is not None and y is None and z is None:
            self.scale = [float(x)] * 3
        else:
            if x is not None: self.scale[0] = float(x)
            if y is not None: self.scale[1] = float(y)
            if z is not None: self.scale[2] = float(z)
        return self

    def world_vertices(self):
        """Vertices after scale -> rotation -> position are applied."""
        rx, ry, rz = (math.radians(a) for a in self.rotation)
        sx_, sy_, sz_ = self.scale
        px, py, pz = self.position
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        out = []
        for vx, vy, vz in self.vertices:
            x, y, z = vx * sx_, vy * sy_, vz * sz_
            y, z = y * cx - z * sx, y * sx + z * cx          # around x
            x, z = x * cy + z * sy, -x * sy + z * cy         # around y
            x, y = x * cz - y * sz, x * sz + y * cz          # around z
            out.append((x + px, y + py, z + pz))
        return out


# --------------------------------------------------------------- primitives

def box(width=1.0, height=1.0, depth=1.0, color="#4f8ef7", name="box"):
    """A rectangular box centered on its position."""
    x, y, z = width / 2, height / 2, depth / 2
    verts = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
        (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5),
    ]
    return Mesh(verts, faces, color=color, name=name)


def cube(size=1.0, color="#4f8ef7", name="cube"):
    """A cube (same as box with equal sides)."""
    return box(size, size, size, color=color, name=name)


def sphere(radius=1.0, detail=10, color="#e06666", name="sphere"):
    """A sphere. Higher detail = smoother (and slower)."""
    stacks = max(3, int(detail))
    slices = max(3, int(detail) * 2)
    verts = []
    for i in range(stacks + 1):
        phi = math.pi * i / stacks
        y = radius * math.cos(phi)
        r = radius * math.sin(phi)
        for j in range(slices):
            theta = 2 * math.pi * j / slices
            verts.append((r * math.cos(theta), y, r * math.sin(theta)))
    faces = []
    for i in range(stacks):
        for j in range(slices):
            a = i * slices + j
            b = i * slices + (j + 1) % slices
            c = (i + 1) * slices + (j + 1) % slices
            d = (i + 1) * slices + j
            if i == 0:
                faces.append((a, c, d))
            elif i == stacks - 1:
                faces.append((a, b, d))
            else:
                faces.append((a, b, c, d))
    return Mesh(verts, faces, color=color, name=name)


def cylinder(radius=0.5, height=1.0, sides=16, color="#f7b84f", name="cylinder"):
    """A cylinder standing on the y axis."""
    sides = max(3, int(sides))
    h = height / 2
    verts = []
    for j in range(sides):
        theta = 2 * math.pi * j / sides
        verts.append((radius * math.cos(theta), h, radius * math.sin(theta)))
    for j in range(sides):
        theta = 2 * math.pi * j / sides
        verts.append((radius * math.cos(theta), -h, radius * math.sin(theta)))
    top_c, bot_c = len(verts), len(verts) + 1
    verts += [(0, h, 0), (0, -h, 0)]
    faces = []
    for j in range(sides):
        k = (j + 1) % sides
        faces.append((j, k, sides + k, sides + j))       # side wall
        faces.append((top_c, j, k))                      # top cap slice
        faces.append((bot_c, sides + j, sides + k))      # bottom cap slice
    return Mesh(verts, faces, color=color, name=name)


def cone(radius=0.6, height=1.0, sides=16, color="#9d6bf5", name="cone"):
    """A cone pointing up."""
    sides = max(3, int(sides))
    h = height / 2
    verts = [(radius * math.cos(2 * math.pi * j / sides), -h,
              radius * math.sin(2 * math.pi * j / sides)) for j in range(sides)]
    apex, base_c = len(verts), len(verts) + 1
    verts += [(0, h, 0), (0, -h, 0)]
    faces = []
    for j in range(sides):
        k = (j + 1) % sides
        faces.append((apex, j, k))
        faces.append((base_c, j, k))
    return Mesh(verts, faces, color=color, name=name)


def pyramid(size=1.0, color="#4fbf9f", name="pyramid"):
    """A square pyramid."""
    s, h = size / 2, size / 2
    verts = [(-s, -h, -s), (s, -h, -s), (s, -h, s), (-s, -h, s), (0, h, 0)]
    faces = [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    return Mesh(verts, faces, color=color, name=name)


def plane(width=4.0, depth=4.0, color="#3a3d46", name="plane"):
    """A flat rectangle lying on the ground (y = 0)."""
    x, z = width / 2, depth / 2
    return Mesh([(-x, 0, -z), (x, 0, -z), (x, 0, z), (-x, 0, z)],
                [(0, 1, 2, 3)], color=color, name=name)


# ----------------------------------------------------------------- the view

def _normalize(x, y, z):
    n = math.sqrt(x * x + y * y + z * z) or 1.0
    return x / n, y / n, z / n


class View3D(tk.Canvas, EasyWidget):
    """A 3D viewport widget. Add meshes to it, drag it around with the mouse.

    Camera:  .yaw / .pitch (degrees), .distance, .target, .fov — or just use
    the mouse: left-drag orbits, scroll zooms, right- or shift-drag pans.
    """

    _layout_defaults = {"fill": "both", "expand": True}

    def __init__(self, parent, width=220, height=160, background=None,
                 grid=True, axes=True, controls=True, fov=60, **kw):
        # width/height are just the *minimum* — the view normally expands
        # to fill whatever space its container gives it
        theme = get_theme(parent)
        self._theme = theme
        super().__init__(parent, width=width, height=height,
                         bg=background or theme["canvas_bg"],
                         highlightthickness=0, **kw)
        self.meshes = []
        self.yaw = 40.0
        self.pitch = 22.0
        self.distance = 7.0
        self.target = [0.0, 0.0, 0.0]
        self.fov = fov
        self.show_grid = grid
        self.show_axes = axes
        self.grid_size = 5
        self.light = _normalize(-0.45, 0.75, -0.55)
        self.ambient = 0.35
        self.on_frame = None           # called every animation frame, if set

        self._spins = {}
        self._fps = 60
        self._animating = False
        self._after_id = None
        self._mouse = None
        self.bind("<Destroy>", self._on_destroy, add="+")

        if controls:
            self.bind("<ButtonPress-1>", self._press)
            self.bind("<B1-Motion>", lambda e: self._drag(e, pan=False))
            self.bind("<Shift-B1-Motion>", lambda e: self._drag(e, pan=True))
            self.bind("<ButtonPress-3>", self._press)
            self.bind("<B3-Motion>", lambda e: self._drag(e, pan=True))
            self.bind("<ButtonPress-2>", self._press)
            self.bind("<B2-Motion>", lambda e: self._drag(e, pan=True))
            self.bind("<MouseWheel>", self._wheel)          # windows / mac
            self.bind("<Button-4>", lambda e: self.zoom(0.9))   # linux
            self.bind("<Button-5>", lambda e: self.zoom(1.1))
        self.bind("<Configure>", lambda e: self.render())

    # --- adding stuff ---

    def add(self, mesh):
        """Add any Mesh to the scene."""
        self.meshes.append(mesh)
        self.render()
        return mesh

    def add_cube(self, size=1.0, **kw):        return self.add(cube(size, **kw))
    def add_box(self, w=1.0, h=1.0, d=1.0, **kw): return self.add(box(w, h, d, **kw))
    def add_sphere(self, radius=1.0, **kw):    return self.add(sphere(radius, **kw))
    def add_cylinder(self, radius=0.5, height=1.0, **kw): return self.add(cylinder(radius, height, **kw))
    def add_cone(self, radius=0.6, height=1.0, **kw): return self.add(cone(radius, height, **kw))
    def add_pyramid(self, size=1.0, **kw):     return self.add(pyramid(size, **kw))
    def add_plane(self, width=4.0, depth=4.0, **kw): return self.add(plane(width, depth, **kw))

    def add_mesh(self, vertices, faces, **kw):
        """Build a custom Mesh from raw vertices + faces and add it."""
        return self.add(Mesh(vertices, faces, **kw))

    def remove(self, mesh):
        if mesh in self.meshes:
            self.meshes.remove(mesh)
        self._spins.pop(mesh, None)
        self.render()

    def clear(self):
        """Remove every mesh."""
        self.meshes.clear()
        self._spins.clear()
        self.render()

    # --- camera ---

    def look_at(self, x=0.0, y=0.0, z=0.0):
        """Point the camera at a spot."""
        self.target = [float(x), float(y), float(z)]
        self.render()
        return self

    def zoom(self, factor):
        """< 1 zooms in, > 1 zooms out."""
        self.distance = max(0.5, min(500.0, self.distance * factor))
        self.render()

    # --- animation ---

    def spin(self, mesh, x=0.0, y=0.0, z=0.0):
        """Keep a mesh rotating by (x, y, z) degrees every frame."""
        self._spins[mesh] = (x, y, z)
        self._start_animating()
        return mesh

    def stop_spin(self, mesh=None):
        """Stop one mesh spinning (or all of them if no mesh given)."""
        if mesh is None:
            self._spins.clear()
        else:
            self._spins.pop(mesh, None)

    def animate(self, fn=None, fps=60):
        """Run fn() every frame (and keep the view re-rendering)."""
        if fn is not None:
            self.on_frame = fn
        self._fps = max(1, int(fps))
        self._start_animating()
        return self

    def stop(self):
        """Stop the animation loop entirely."""
        self._animating = False
        self._spins.clear()
        self.on_frame = None

    def _start_animating(self):
        if not self._animating:
            self._animating = True
            self._tick()

    def _tick(self):
        self._after_id = None
        if not self._animating:
            return
        try:
            if not self.winfo_exists():
                return
            for mesh, (dx, dy, dz) in list(self._spins.items()):
                mesh.rotate(dx, dy, dz)
            if self.on_frame:
                self.on_frame()
            self.render()
            self._after_id = self.after(max(1, int(1000 / self._fps)), self._tick)
        except tk.TclError:
            self._animating = False

    def _on_destroy(self, _event=None):
        self._animating = False
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    # --- mouse ---

    def _press(self, event):
        self._mouse = (event.x, event.y)

    def _drag(self, event, pan):
        if self._mouse is None:
            self._mouse = (event.x, event.y)
            return
        dx = event.x - self._mouse[0]
        dy = event.y - self._mouse[1]
        self._mouse = (event.x, event.y)
        if pan:
            right, up = self._camera_axes()
            s = self.distance * 0.0022
            for i in range(3):
                self.target[i] += (-dx * right[i] + dy * up[i]) * s
        else:
            self.yaw = (self.yaw + dx * 0.45) % 360
            self.pitch = max(-89.0, min(89.0, self.pitch + dy * 0.45))
        self.render()

    def _wheel(self, event):
        self.zoom(0.9 if event.delta > 0 else 1.1)

    def _camera_axes(self):
        """World-space right and up vectors of the camera (for panning)."""
        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        right = (cy, 0.0, -sy)
        up = (-sy * sp, cp, -cy * sp)
        return right, up

    # --- rendering ---

    def render(self):
        """Redraw the scene right now (usually happens automatically)."""
        try:
            self.delete("all")
        except tk.TclError:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:   # not laid out yet -> use requested size
            w = int(self["width"])
            h = int(self["height"])
        cx, cy = w / 2, h / 2
        focal = (h / 2) / math.tan(math.radians(self.fov) / 2)

        yaw, pitch = math.radians(self.yaw), math.radians(self.pitch)
        cyw, syw = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        tx, ty, tz = self.target
        dist = self.distance
        near = 0.05

        def to_view(p):
            x, y, z = p[0] - tx, p[1] - ty, p[2] - tz
            x, z = x * cyw - z * syw, x * syw + z * cyw
            y, z = y * cp - z * sp, y * sp + z * cp
            return x, y, z + dist

        def project(v):
            s = focal / v[2]
            return cx + v[0] * s, cy - v[1] * s

        if self.show_grid:
            self._draw_grid(to_view, project, near)
        if self.show_axes:
            self._draw_axes(to_view, project, near)

        # collect every visible face with its depth
        lx, ly, lz = self.light
        ambient = self.ambient
        polys = []
        for mesh in self.meshes:
            if not mesh.visible:
                continue
            view = [to_view(p) for p in mesh.world_vertices()]
            for face in mesh.faces:
                pts = [view[i] for i in face]
                if any(p[2] <= near for p in pts):
                    continue
                depth = sum(p[2] for p in pts) / len(pts)
                if mesh.wireframe:
                    fill, edge = "", mesh.color
                else:
                    # flat shading from the face normal
                    ax, ay, az = pts[0]
                    ux, uy, uz = pts[1][0] - ax, pts[1][1] - ay, pts[1][2] - az
                    vx, vy, vz = pts[2][0] - ax, pts[2][1] - ay, pts[2][2] - az
                    nx = uy * vz - uz * vy
                    ny = uz * vx - ux * vz
                    nz = ux * vy - uy * vx
                    if nz > 0:   # flip so the normal faces the camera
                        nx, ny, nz = -nx, -ny, -nz
                    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                    lit = max(0.0, (nx * lx + ny * ly + nz * lz) / n)
                    fill = shade(mesh.color, ambient + (1 - ambient) * lit)
                    if mesh.outline is False:
                        edge = fill
                    elif mesh.outline:
                        edge = mesh.outline
                    else:
                        edge = shade(fill, 0.82)
                screen = []
                for p in pts:
                    screen.extend(project(p))
                polys.append((depth, screen, fill, edge))

        polys.sort(key=lambda item: item[0], reverse=True)   # far -> near
        for _, screen, fill, edge in polys:
            self.create_polygon(*screen, fill=fill, outline=edge, width=1)

    def _draw_grid(self, to_view, project, near):
        g = int(self.grid_size)
        color = self._theme["grid"]
        for i in range(-g, g + 1):
            for a, b in (((i, 0, -g), (i, 0, g)), ((-g, 0, i), (g, 0, i))):
                va, vb = to_view(a), to_view(b)
                if va[2] <= near or vb[2] <= near:
                    continue
                self.create_line(*project(va), *project(vb), fill=color)

    def _draw_axes(self, to_view, project, near):
        theme = self._theme
        origin = to_view((0, 0, 0))
        if origin[2] <= near:
            return
        for end, color in (((2, 0, 0), theme["axis_x"]),
                           ((0, 2, 0), theme["axis_y"]),
                           ((0, 0, 2), theme["axis_z"])):
            v = to_view(end)
            if v[2] <= near:
                continue
            self.create_line(*project(origin), *project(v), fill=color, width=2)
