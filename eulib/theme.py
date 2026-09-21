"""Themes + color helpers for eulib."""

THEMES = {
    "dark": {
        "bg": "#1e1f24",          # window background
        "panel": "#2a2c33",       # raised surfaces (rows/columns with a bg, toasts)
        "fg": "#e8e9ed",          # main text
        "subtle": "#9aa0ab",      # placeholder / secondary text
        "accent": "#4f8ef7",      # buttons, highlights
        "accent_active": "#6ba1f8",
        "accent_fg": "#ffffff",   # text on accent
        "entry_bg": "#15161a",    # inputs, dropdowns, textboxes
        "border": "#3a3d46",
        "canvas_bg": "#111216",   # 3d view background
        "grid": "#2e3138",
        "axis_x": "#e05555",
        "axis_y": "#4fbf67",
        "axis_z": "#4f8ef7",
    },
    "light": {
        "bg": "#f2f3f6",
        "panel": "#ffffff",
        "fg": "#17181c",
        "subtle": "#6a707c",
        "accent": "#2f6fe4",
        "accent_active": "#4b84ea",
        "accent_fg": "#ffffff",
        "entry_bg": "#ffffff",
        "border": "#d4d7de",
        "canvas_bg": "#e9ebf0",
        "grid": "#d0d3da",
        "axis_x": "#d64545",
        "axis_y": "#2f9e4f",
        "axis_z": "#2f6fe4",
    },
}

DEFAULT_THEME = "dark"


def get_theme(widget):
    """Find the theme of the window a widget lives in (falls back to dark)."""
    try:
        top = widget.winfo_toplevel()
        theme = getattr(top, "_eulib_theme", None)
        if theme:
            return theme
    except Exception:
        pass
    return THEMES[DEFAULT_THEME]


def hex_to_rgb(color):
    """'#4f8ef7' -> (79, 142, 247). Also accepts short form '#48f'."""
    c = str(color).lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def rgb_to_hex(r, g, b):
    clamp = lambda v: max(0, min(255, int(round(v))))
    return "#{:02x}{:02x}{:02x}".format(clamp(r), clamp(g), clamp(b))


def shade(color, factor):
    """Darken (factor < 1) or lighten (factor > 1) a hex color."""
    r, g, b = hex_to_rgb(color)
    if factor <= 1:
        return rgb_to_hex(r * factor, g * factor, b * factor)
    # lighten: blend toward white
    t = min(1.0, factor - 1.0)
    return rgb_to_hex(r + (255 - r) * t, g + (255 - g) * t, b + (255 - b) * t)
