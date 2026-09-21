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

from .base import EasyWidget, font, parent_bg, take_pack
from .theme import get_theme
from .view3d import View3D


# ---------------------------------------------------------------- widgets

class Label(tk.Label, EasyWidget):
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

class WidgetFactory:
    """Everything a window, row, or column can create. Each method makes the
    widget, lays it out, and returns it.

    All of them accept layout keywords too: side, fill, expand, anchor,
    pad / padx / pady.
    """

    _side = "top"   # which way children stack by default

    def _content(self):
        return self

    def _place(self, widget, defaults, pack):
        parent = widget.master
        merged = dict(defaults)
        merged.update(pack)
        side = merged.pop("side", None) or getattr(parent, "_side", "top")
        pad = merged.pop("pad", 6)
        merged.setdefault("padx", pad)
        merged.setdefault("pady", pad)
        widget.pack(side=side, **merged)
        widget._pack_opts = dict(side=side, **merged)
        return widget

    # --- text ---

    def label(self, text="", **opts):
        pack = take_pack(opts)
        return self._place(Label(self._content(), text=text, **opts),
                           {"anchor": "w"}, pack)

    def heading(self, text="", size=17, **opts):
        """A big bold label."""
        opts.setdefault("bold", True)
        pack = take_pack(opts)
        return self._place(Label(self._content(), text=text, size=size, **opts),
                           {"anchor": "w"}, pack)

    # --- controls ---

    def button(self, text="Button", on_click=None, **opts):
        pack = take_pack(opts)
        return self._place(Button(self._content(), text=text, on_click=on_click,
                                  **opts), {"anchor": "w"}, pack)

    def input(self, placeholder="", **opts):
        pack = take_pack(opts)
        return self._place(Input(self._content(), placeholder=placeholder,
                                 **opts), {"fill": "x", "anchor": "w"}, pack)

    entry = input  # tkinter folks expect .entry()

    def dropdown(self, options=(), on_select=None, **opts):
        pack = take_pack(opts)
        return self._place(Dropdown(self._content(), options=options,
                                    on_select=on_select, **opts),
                           {"anchor": "w"}, pack)

    def slider(self, min=0, max=100, **opts):
        pack = take_pack(opts)
        return self._place(Slider(self._content(), min=min, max=max, **opts),
                           {"fill": "x", "anchor": "w"}, pack)

    def checkbox(self, text="", **opts):
        pack = take_pack(opts)
        return self._place(Checkbox(self._content(), text=text, **opts),
                           {"anchor": "w"}, pack)

    def textbox(self, value="", **opts):
        pack = take_pack(opts)
        return self._place(TextBox(self._content(), value=value, **opts),
                           {"fill": "x", "anchor": "w"}, pack)

    # --- layout ---

    def row(self, **opts):
        """A container whose children line up left-to-right."""
        pack = take_pack(opts)
        return self._place(Row(self._content(), **opts), {"fill": "x"}, pack)

    def column(self, **opts):
        """A container whose children stack top-to-bottom."""
        pack = take_pack(opts)
        return self._place(Column(self._content(), **opts),
                           {"fill": "both", "expand": True}, pack)

    def separator(self, **opts):
        pack = take_pack(opts)
        horizontal = getattr(self._content(), "_side", "top") in ("top", "bottom")
        sep = ttk.Separator(self._content(),
                            orient="horizontal" if horizontal else "vertical")
        return self._place(sep, {"fill": "x" if horizontal else "y"}, pack)

    def spacer(self, size=10, **opts):
        pack = take_pack(opts)
        frame = tk.Frame(self._content(), width=size, height=size,
                         bg=parent_bg(self._content()))
        return self._place(frame, {"pad": 0}, pack)

    # --- 3d ---

    def view3d(self, **opts):
        """A 3D viewport (see View3D). Fills the space it's given."""
        pack = take_pack(opts)
        return self._place(View3D(self._content(), **opts),
                           {"fill": "both", "expand": True}, pack)


class Row(tk.Frame, WidgetFactory, EasyWidget):
    """Children added to a Row go side by side."""
    _side = "left"

    def __init__(self, parent, background=None, **kw):
        super().__init__(parent, bg=background or parent_bg(parent), **kw)


class Column(tk.Frame, WidgetFactory, EasyWidget):
    """Children added to a Column stack downward."""
    _side = "top"

    def __init__(self, parent, background=None, **kw):
        super().__init__(parent, bg=background or parent_bg(parent), **kw)
