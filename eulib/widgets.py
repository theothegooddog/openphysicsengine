"""
eulib widgets — tkinter widgets with training wheels.

You normally don't create these directly; any window / row / column makes
them for you and lays them out automatically:

    window.label("hi")
    window.button("Click", on_click=fn)
    window.dropdown(["a", "b"], on_select=fn)

Every widget has .hide() / .show() / .enable() / .disable(), and the ones
that hold something have a .value you can read and write.
"""

import tkinter as tk
from tkinter import ttk

from .base import EasyWidget, font, parent_bg, raise_tree, take_pack
from .theme import get_theme
from .view3d import View3D


# ---------------------------------------------------------------- widgets

class Label(tk.Label, EasyWidget):
    _layout_defaults = {"anchor": "w"}

    def __init__(self, parent, text="", size=11, bold=False, color=None, **kw):
        theme = get_theme(parent)
        kw.setdefault("justify", "left")
        super().__init__(parent, text=text, font=font(size, bold),
                         bg=parent_bg(parent), fg=color or theme["fg"], **kw)

    @property
    def text(self):
        return self.cget("text")

    @text.setter
    def text(self, value):
        self.configure(text=value)


class Button(tk.Button, EasyWidget):
    _layout_defaults = {"anchor": "w"}

    def __init__(self, parent, text="Button", on_click=None, color=None,
                 text_color=None, size=11, **kw):
        theme = get_theme(parent)
        self.on_click = on_click
        bg = color or theme["accent"]
        super().__init__(parent, text=text, command=self._clicked,
                         font=font(size), bg=bg, fg=text_color or theme["accent_fg"],
                         activebackground=theme["accent_active"],
                         activeforeground=text_color or theme["accent_fg"],
                         relief="flat", bd=0, padx=14, pady=6,
                         cursor="hand2", highlightthickness=0, **kw)

    def _clicked(self):
        if self.on_click:
            self.on_click()

    def click(self):
        """Press the button from code."""
        self._clicked()

    @property
    def text(self):
        return self.cget("text")

    @text.setter
    def text(self, value):
        self.configure(text=value)


class Input(tk.Entry, EasyWidget):
    """A text box with optional placeholder text.

    input.value       -> what's typed (placeholder doesn't count)
    on_change=fn      -> fn(text) as the user types
    on_enter=fn       -> fn(text) when they press Enter
    """

    _layout_defaults = {"fill": "x", "anchor": "w"}

    def __init__(self, parent, placeholder="", value="", on_change=None,
                 on_enter=None, width=24, password=False, **kw):
        theme = get_theme(parent)
        self.on_change = on_change
        self.on_enter = on_enter
        self._placeholder = placeholder
        self._showing_placeholder = False
        self._muted = False
        self._fg = theme["fg"]
        self._subtle = theme["subtle"]
        self._password = password
        self._var = tk.StringVar(value=value)
        super().__init__(parent, textvariable=self._var, width=width,
                         font=font(11), bg=theme["entry_bg"], fg=self._fg,
                         insertbackground=self._fg, relief="flat",
                         highlightthickness=1,
                         highlightbackground=theme["border"],
                         highlightcolor=theme["accent"], **kw)
        if password:
            self.configure(show="•")
        self._var.trace_add("write", self._changed)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.bind("<Return>", self._entered)
        if not value:
            self._focus_out()

    def _set_muted(self, text):
        self._muted = True
        self._var.set(text)
        self._muted = False

    def _changed(self, *_):
        if self._muted or self._showing_placeholder:
            return
        if self.on_change:
            self.on_change(self.value)

    def _entered(self, _event=None):
        if self.on_enter:
            self.on_enter(self.value)

    def _focus_in(self, _event=None):
        if self._showing_placeholder:
            self._showing_placeholder = False
            self._set_muted("")
            self.configure(fg=self._fg, show="•" if self._password else "")

    def _focus_out(self, _event=None):
        if not self._var.get() and self._placeholder:
            self._showing_placeholder = True
            self.configure(fg=self._subtle, show="")
            self._set_muted(self._placeholder)

    @property
    def value(self):
        return "" if self._showing_placeholder else self._var.get()

    @value.setter
    def value(self, text):
        text = str(text)
        if text:
            self._showing_placeholder = False
            self.configure(fg=self._fg, show="•" if self._password else "")
            self._var.set(text)
        else:
            self._set_muted("")
            self._focus_out()

    def clear(self):
        self.value = ""


class Dropdown(ttk.Combobox, EasyWidget):
    """A pick-one-option menu.

    dropdown.value    -> the selected option
    dropdown.options  -> the list of options (you can assign a new list)
    on_select=fn      -> fn(choice) when the user picks something
    """

    _layout_defaults = {"anchor": "w"}

    def __init__(self, parent, options=(), value=None, on_select=None,
                 width=None, **kw):
        self.on_select = on_select
        options = [str(o) for o in options]
        kw.setdefault("state", "readonly")
        if width is None:
            width = max([len(o) for o in options] + [8]) + 2
        super().__init__(parent, values=options, width=width, font=font(11), **kw)
        if value is not None:
            self.set(str(value))
        elif options:
            self.set(options[0])
        self.bind("<<ComboboxSelected>>", self._selected)

    def _selected(self, _event=None):
        self.selection_clear()
        if self.on_select:
            self.on_select(self.value)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, choice):
        self.set(str(choice))

    @property
    def options(self):
        return list(self.cget("values"))

    @options.setter
    def options(self, options):
        options = [str(o) for o in options]
        self.configure(values=options)
        if self.get() not in options:
            self.set(options[0] if options else "")


class Slider(tk.Scale, EasyWidget):
    """Drag to pick a number between min and max.

    slider.value  -> the current number
    on_change=fn  -> fn(number) while dragging
    """

    _layout_defaults = {"fill": "x", "anchor": "w"}

    def __init__(self, parent, min=0, max=100, value=None, step=None,
                 label="", on_change=None, horizontal=True, length=180, **kw):
        theme = get_theme(parent)
        self.on_change = on_change
        if step is None:
            span = max - min
            step = 1 if (isinstance(min, int) and isinstance(max, int)
                         and span >= 10) else span / 100.0
        super().__init__(parent, from_=min, to=max, resolution=step,
                         label=label or None,
                         orient="horizontal" if horizontal else "vertical",
                         length=length, command=self._changed, font=font(9),
                         bg=parent_bg(parent), fg=theme["fg"],
                         troughcolor=theme["entry_bg"],
                         activebackground=theme["accent_active"],
                         highlightthickness=0, bd=0, **kw)
        self._initial = float(min if value is None else value)
        self._settled = False
        self.set(self._initial)

    def _changed(self, raw):
        # tk fires the command once for the starting value; skip that one
        if not self._settled:
            self._settled = True
            if float(raw) == self._initial:
                return
        if self.on_change:
            self.on_change(float(raw))

    @property
    def value(self):
        return float(self.get())

    @value.setter
    def value(self, number):
        self.set(number)


class Checkbox(tk.Checkbutton, EasyWidget):
    """A tick box. checkbox.checked is True/False; on_toggle=fn gets fn(bool)."""

    _layout_defaults = {"anchor": "w"}

    def __init__(self, parent, text="", checked=False, on_toggle=None, **kw):
        theme = get_theme(parent)
        self.on_toggle = on_toggle
        self._var = tk.BooleanVar(value=bool(checked))
        bg = parent_bg(parent)
        super().__init__(parent, text=text, variable=self._var,
                         command=self._toggled, font=font(11),
                         bg=bg, fg=theme["fg"], activebackground=bg,
                         activeforeground=theme["fg"],
                         selectcolor=theme["entry_bg"],
                         highlightthickness=0, anchor="w", **kw)

    def _toggled(self):
        if self.on_toggle:
            self.on_toggle(self._var.get())

    @property
    def checked(self):
        return self._var.get()

    @checked.setter
    def checked(self, on):
        self._var.set(bool(on))

    value = checked  # .value works too


class TextBox(tk.Text, EasyWidget):
    """A multi-line text area. Great as a log with readonly=True + .append()."""

    _layout_defaults = {"fill": "x", "anchor": "w"}

    def __init__(self, parent, value="", readonly=False, height=6, width=36, **kw):
        theme = get_theme(parent)
        self._readonly = readonly
        super().__init__(parent, height=height, width=width, font=font(10),
                         bg=theme["entry_bg"], fg=theme["fg"],
                         insertbackground=theme["fg"], relief="flat",
                         highlightthickness=1,
                         highlightbackground=theme["border"],
                         highlightcolor=theme["accent"], wrap="word",
                         padx=6, pady=6, **kw)
        if value:
            self.insert("1.0", value)
        if readonly:
            self.configure(state="disabled")

    @property
    def value(self):
        return self.get("1.0", "end-1c")

    @value.setter
    def value(self, text):
        state = self.cget("state")
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", str(text))
        self.configure(state=state)

    def append(self, text):
        """Add a line to the end (and scroll to it)."""
        state = self.cget("state")
        self.configure(state="normal")
        if self.value:
            self.insert("end", "\n")
        self.insert("end", str(text))
        self.see("end")
        self.configure(state=state)


# ----------------------------------------------------- containers + factory

def _detach(widget):
    """Take a widget out of whatever layout it's currently in."""
    manager = widget.winfo_manager()
    if manager == "pack":
        widget.pack_forget()
    elif manager == "place":
        widget.place_forget()
    elif manager == "grid":
        widget.grid_forget()


def _flatten(items):
    """add(a, b) and add([a, b]) both work."""
    out = []
    for item in items:
        if isinstance(item, (list, tuple)):
            out.extend(item)
        else:
            out.append(item)
    return out


# where each anchor sits inside a Stack, as (relx, rely)
_ANCHOR_POS = {
    "center": (0.5, 0.5), "n": (0.5, 0.0), "s": (0.5, 1.0),
    "e": (1.0, 0.5), "w": (0.0, 0.5),
    "ne": (1.0, 0.0), "nw": (0.0, 0.0), "se": (1.0, 1.0), "sw": (0.0, 1.0),
}


class WidgetFactory:
    """Everything a window, row, column, or stack can create. Each method
    makes the widget, lays it out, and returns it.

    All of them accept layout keywords too: side, fill, expand, anchor,
    pad / padx / pady.
    """

    _side = "top"   # which way children stack by default

    def _content(self):
        return self

    def _place(self, widget, pack, defaults=None):
        if defaults is None:
            defaults = getattr(widget, "_layout_defaults", {})
        merged = dict(defaults)
        merged.update(pack)
        side = merged.pop("side", None) or getattr(widget.master, "_side", "top")
        pad = merged.pop("pad", 6)
        merged.setdefault("padx", pad)
        merged.setdefault("pady", pad)
        widget.pack(side=side, **merged)
        widget._geo = ("pack", dict(side=side, **merged))
        return widget

    # --- text ---

    def label(self, text="", **opts):
        pack = take_pack(opts)
        return self._place(Label(self._content(), text=text, **opts), pack)

    def heading(self, text="", size=17, **opts):
        """A big bold label."""
        opts.setdefault("bold", True)
        pack = take_pack(opts)
        return self._place(Label(self._content(), text=text, size=size, **opts),
                           pack)

    # --- controls ---

    def button(self, text="Button", on_click=None, **opts):
        pack = take_pack(opts)
        return self._place(Button(self._content(), text=text,
                                  on_click=on_click, **opts), pack)

    def input(self, placeholder="", **opts):
        pack = take_pack(opts)
        return self._place(Input(self._content(), placeholder=placeholder,
                                 **opts), pack)

    entry = input  # tkinter folks expect .entry()

    def dropdown(self, options=(), on_select=None, **opts):
        pack = take_pack(opts)
        return self._place(Dropdown(self._content(), options=options,
                                    on_select=on_select, **opts), pack)

    def slider(self, min=0, max=100, **opts):
        pack = take_pack(opts)
        return self._place(Slider(self._content(), min=min, max=max, **opts),
                           pack)

    def checkbox(self, text="", **opts):
        pack = take_pack(opts)
        return self._place(Checkbox(self._content(), text=text, **opts), pack)

    def textbox(self, value="", **opts):
        pack = take_pack(opts)
        return self._place(TextBox(self._content(), value=value, **opts), pack)

    # --- layout ---

    def add(self, *items, gap=6):
        """Move widgets you already made into this container.

        The widgets must have been created from this same window (or from
        one of its rows/columns on the same branch) — which is where they
        come from anyway.
        """
        target = self._content()
        side = getattr(target, "_side", "top")
        for widget in _flatten(items):
            _detach(widget)
            opts = dict(getattr(widget, "_layout_defaults", {}))
            opts.setdefault("padx", gap)
            opts.setdefault("pady", gap)
            try:
                widget.pack(in_=target, side=side, **opts)
            except tk.TclError as err:
                raise ValueError(
                    f"can't move {widget.__class__.__name__} here — widgets "
                    "can only be grouped into containers made from the same "
                    f"window/row/column they were created on ({err})"
                ) from err
            raise_tree(widget)
            widget._geo = ("pack", dict(in_=target, side=side, **opts))
        return self

    def row(self, **opts):
        """A container whose children line up left-to-right."""
        pack = take_pack(opts)
        return self._place(Row(self._content(), **opts), pack)

    def column(self, **opts):
        """A container whose children stack top-to-bottom."""
        pack = take_pack(opts)
        return self._place(Column(self._content(), **opts), pack)

    def vertical(self, items=None, gap=6, **opts):
        """A column of widgets you already made, top to bottom:

            window.vertical([view_a, view_b, view_c])
        """
        pack = take_pack(opts)
        column = self._place(Column(self._content(), **opts), pack)
        if items is not None:
            column.add(items, gap=gap)
        return column

    def horizontal(self, items=None, gap=6, **opts):
        """A row of widgets you already made, left to right:

            window.horizontal([view_a, view_b])
        """
        pack = take_pack(opts)
        row = self._place(Row(self._content(), **opts), pack,
                          {"fill": "both", "expand": True})
        if items is not None:
            row.add(items, gap=gap)
        return row

    def stack(self, items=None, **opts):
        """Widgets on top of each other in the same place. The first item is
        the base and fills the stack; the rest float over it (centered, or
        give a (widget, anchor) pair):

            window.stack([view, (fps_label, "nw")])
        """
        pack = take_pack(opts)
        the_stack = self._place(Stack(self._content(), **opts), pack)
        if items is not None:
            the_stack.add(items)
        return the_stack

    def separator(self, **opts):
        pack = take_pack(opts)
        horizontal = getattr(self._content(), "_side", "top") in ("top", "bottom")
        sep = ttk.Separator(self._content(),
                            orient="horizontal" if horizontal else "vertical")
        return self._place(sep, pack, {"fill": "x" if horizontal else "y"})

    def spacer(self, size=10, **opts):
        pack = take_pack(opts)
        frame = tk.Frame(self._content(), width=size, height=size,
                         bg=parent_bg(self._content()))
        return self._place(frame, pack, {"pad": 0})

    # --- 3d ---

    def view3d(self, **opts):
        """A 3D viewport (see View3D). Fills the space it's given."""
        pack = take_pack(opts)
        return self._place(View3D(self._content(), **opts), pack)


class Row(tk.Frame, WidgetFactory, EasyWidget):
    """Children added to a Row go side by side."""
    _side = "left"
    _layout_defaults = {"fill": "x"}

    def __init__(self, parent, background=None, **kw):
        super().__init__(parent, bg=background or parent_bg(parent), **kw)


class Column(tk.Frame, WidgetFactory, EasyWidget):
    """Children added to a Column stack downward."""
    _side = "top"
    _layout_defaults = {"fill": "both", "expand": True}

    def __init__(self, parent, background=None, **kw):
        super().__init__(parent, bg=background or parent_bg(parent), **kw)


class Stack(tk.Frame, WidgetFactory, EasyWidget):
    """Widgets layered in the same place. The first widget is the base and
    fills the whole stack (it also decides the stack's size); every later
    widget floats on top of it.

        hud = window.stack([view, (label, "nw")])
        hud.add(button, anchor="se")            # or with an offset:
        hud.add(minimap, anchor="ne", x=-4, y=4)

    Anchors: center (default), n, s, e, w, ne, nw, se, sw.
    Edge anchors get a small margin built in; x / y nudge from there.
    """

    _layout_defaults = {"fill": "both", "expand": True}

    def __init__(self, parent, background=None, **kw):
        super().__init__(parent, bg=background or parent_bg(parent), **kw)
        self.base = None

    @staticmethod
    def _layers(items):
        # flatten lists only — tuples stay whole, they mean (widget, anchor)
        out = []
        for item in items:
            if isinstance(item, list):
                out.extend(item)
            else:
                out.append(item)
        return out

    def add(self, *items, anchor="center", x=0, y=0, fill=False):
        """Add widgets to the stack (first ever added becomes the base).

        anchor says where an overlay sits; fill=True makes it cover the
        whole stack (e.g. a pause screen).
        """
        for item in self._layers(items):
            widget, a = item if isinstance(item, tuple) else (item, anchor)
            if a not in _ANCHOR_POS:
                raise ValueError(f"unknown anchor {a!r} — pick one of "
                                 f"{', '.join(_ANCHOR_POS)}")
            _detach(widget)
            try:
                if self.base is None:
                    self.base = widget
                    opts = dict(in_=self, fill="both", expand=True)
                    widget.pack(**opts)
                    widget._geo = ("pack", opts)
                elif fill:
                    opts = dict(in_=self, relx=0, rely=0,
                                relwidth=1, relheight=1)
                    widget.place(**opts)
                    widget._geo = ("place", opts)
                else:
                    relx, rely = _ANCHOR_POS[a]
                    if a == "center":
                        dx = dy = 0
                    else:
                        dx = 10 if "w" in a else (-10 if "e" in a else 0)
                        dy = 10 if "n" in a else (-10 if "s" in a else 0)
                    opts = dict(in_=self, relx=relx, rely=rely,
                                x=x + dx, y=y + dy, anchor=a)
                    widget.place(**opts)
                    widget._geo = ("place", opts)
            except tk.TclError as err:
                raise ValueError(
                    f"can't stack {widget.__class__.__name__} here — widgets "
                    "can only be grouped into containers made from the same "
                    f"window/row/column they were created on ({err})"
                ) from err
            raise_tree(widget)
        return self

    def _place(self, widget, pack, defaults=None):
        # widgets created *on* the stack (stack.label(...)) become layers:
        # the first is the base, later ones float at their anchor
        self.add(widget, anchor=pack.get("anchor", "center"))
        return widget
