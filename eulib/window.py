"""
The finalui window — eulib's version of tk.Tk().

    from eulib import finalui

    window = finalui.run(title="My App")
    window.label("Hello!")
    window.button("Click me", on_click=lambda: window.toast("hi"))

finalui.run() gives you the window immediately so you can add widgets to it,
and the event loop starts by itself when your script reaches the end — no
mainloop() to remember. (Call window.loop() yourself if you want it sooner,
or finalui.run(auto=False) if you don't want the magic at all.)
"""

import atexit
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .base import EasyWidget, parent_bg
from .theme import DEFAULT_THEME, THEMES
from .widgets import WidgetFactory


class Repeater:
    """A repeating timer made by window.every(ms, fn). Call .stop() to end it."""

    def __init__(self, widget, ms, fn):
        self._widget = widget
        self.ms = max(1, int(ms))
        self.fn = fn
        self.running = True
        self._after_id = None
        self._schedule()

    def _schedule(self):
        try:
            self._after_id = self._widget.after(self.ms, self._tick)
        except tk.TclError:
            self.running = False

    def _tick(self):
        self._after_id = None
        if not self.running:
            return
        try:
            self.fn()
        finally:
            if self.running:
                self._schedule()

    def stop(self):
        self.running = False
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def start(self):
        if not self.running:
            self.running = True
            self._schedule()


# friendly key names -> tk key names
_KEY_ALIASES = {
    "enter": "Return", "return": "Return", "esc": "Escape", "escape": "Escape",
    "space": "space", " ": "space", "tab": "Tab", "backspace": "BackSpace",
    "delete": "Delete", "up": "Up", "down": "Down", "left": "Left",
    "right": "Right", "home": "Home", "end": "End",
}


def _key_sequence(key):
    key = str(key)
    if key.startswith("<"):
        return key
    key = _KEY_ALIASES.get(key.lower(), key)
    return f"<KeyPress-{key}>"


class _WindowMixin(WidgetFactory):
    """Stuff both the main window and child windows share."""

    def _setup_body(self, theme, padding, size, title, resizable):
        self._eulib_theme = theme
        self._side = "top"
        self._on_close_callbacks = []
        self._toast_label = None
        self._toast_timer = None
        self._alive = True
        self.title(title)
        self.geometry(f"{int(size[0])}x{int(size[1])}")
        if not resizable:
            self.resizable(False, False)
        self.configure(bg=theme["bg"])
        self._body = tk.Frame(self, bg=theme["bg"])
        self._body.pack(fill="both", expand=True, padx=padding, pady=padding)
        self._body._side = "top"
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _content(self):
        return self._body

    @property
    def theme(self):
        return self._eulib_theme

    # --- timers ---

    def every(self, ms, fn):
        """Run fn every ms milliseconds. Returns a Repeater with .stop()."""
        return Repeater(self, ms, fn)

    def later(self, ms, fn):
        """Run fn once, ms milliseconds from now."""
        return self.after(int(ms), fn)

    # --- events ---

    def on_key(self, key, fn):
        """Call fn() when a key is pressed. on_key('space', jump)"""
        self.bind(_key_sequence(key), lambda _e: fn())
        return self

    def on_close(self, fn):
        """Call fn() right before the window closes."""
        self._on_close_callbacks.append(fn)
        return self

    # --- popups ---

    def alert(self, message, title="Info"):
        messagebox.showinfo(title, message, parent=self)

    def confirm(self, message, title="Are you sure?"):
        """Yes/No popup -> True/False."""
        return bool(messagebox.askyesno(title, message, parent=self))

    def prompt(self, message, title="Input", default=""):
        """Ask the user to type something -> str (or None if cancelled)."""
        return simpledialog.askstring(title, message, parent=self,
                                      initialvalue=default)

    def toast(self, message, ms=2200):
        """A little message that pops up at the bottom and fades away."""
        theme = self._eulib_theme
        if self._toast_timer is not None:
            try:
                self.after_cancel(self._toast_timer)
            except tk.TclError:
                pass
        if self._toast_label is None or not self._toast_label.winfo_exists():
            self._toast_label = tk.Label(self, font=("Helvetica", 10),
                                         bg=theme["panel"], fg=theme["fg"],
                                         padx=14, pady=7)
        self._toast_label.configure(text=str(message))
        self._toast_label.place(relx=0.5, rely=1.0, y=-16, anchor="s")
        self._toast_label.lift()
        self._toast_timer = self.after(int(ms), self._hide_toast)

    def _hide_toast(self):
        self._toast_timer = None
        if self._toast_label is not None and self._toast_label.winfo_exists():
            self._toast_label.place_forget()

    # --- window control ---

    def fullscreen(self, on=True):
        self.attributes("-fullscreen", bool(on))
        return self

    def close(self):
        """Close the window (runs any on_close callbacks first)."""
        for fn in self._on_close_callbacks:
            try:
                fn()
            except Exception:
                pass
        self._alive = False
        try:
            self.destroy()
        except tk.TclError:
            pass


class finalui(tk.Tk, _WindowMixin):
    """The main window. Make one with finalui.run() (or finalui() classic-style).

    It's a real tk.Tk underneath, so anything tkinter can do still works —
    but you mostly won't need it:

        window = finalui.run(title="Demo", size=(900, 600), theme="dark")
        window.heading("Hello")
        window.button("Go", on_click=go)
        view = window.view3d()
        view.spin(view.add_cube(), y=1)
    """

    _open_windows = []
    _loop_started = False

    def __init__(self, title="eulib", size=(900, 600), theme="dark",
                 resizable=True, padding=14, background=None):
        super().__init__()
        colors = dict(THEMES.get(theme, THEMES[DEFAULT_THEME]))
        if background:
            colors["bg"] = background
        self._style_ttk(colors)
        self._setup_body(colors, padding, size, title, resizable)
        finalui._open_windows.append(self)

    @classmethod
    def run(cls, auto=True, **kwargs):
        """Make a window and hand it to you. The event loop starts on its own
        once your script finishes setting things up.
        """
        window = cls(**kwargs)
        if auto:
            _register_autorun()
        return window

    def loop(self):
        """Start the event loop now (blocks until the window closes)."""
        if finalui._loop_started:
            return
        finalui._loop_started = True
        try:
            self.mainloop()
        except KeyboardInterrupt:
            pass

    def child(self, title="window", size=(420, 320), padding=14):
        """Open an extra window that belongs to this one."""
        return ChildWindow(self, title=title, size=size, padding=padding)

    def _style_ttk(self, colors):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground=colors["entry_bg"],
                        background=colors["panel"], foreground=colors["fg"],
                        arrowcolor=colors["fg"], bordercolor=colors["border"],
                        lightcolor=colors["panel"], darkcolor=colors["panel"],
                        insertcolor=colors["fg"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", colors["entry_bg"])],
                  foreground=[("readonly", colors["fg"])],
                  selectbackground=[("readonly", colors["entry_bg"])],
                  selectforeground=[("readonly", colors["fg"])])
        style.configure("TSeparator", background=colors["border"])
        self.option_add("*TCombobox*Listbox.background", colors["entry_bg"])
        self.option_add("*TCombobox*Listbox.foreground", colors["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", colors["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", colors["accent_fg"])


class ChildWindow(tk.Toplevel, _WindowMixin):
    """An extra window made with window.child(). Same easy API as finalui."""

    def __init__(self, master, title="window", size=(420, 320), padding=14):
        super().__init__(master)
        theme = getattr(master.winfo_toplevel(), "_eulib_theme",
                        THEMES[DEFAULT_THEME])
        self._setup_body(theme, padding, size, title, resizable=True)


# --------------------------------------------------- automatic event loop

_autorun_registered = False
_script_crashed = False


def _register_autorun():
    global _autorun_registered
    if _autorun_registered:
        return
    _autorun_registered = True

    original_hook = sys.excepthook

    def hook(exc_type, exc, tb):
        # if the script blew up, don't pop the window over the traceback
        global _script_crashed
        _script_crashed = True
        original_hook(exc_type, exc, tb)

    sys.excepthook = hook
    atexit.register(_autorun)


def _autorun():
    if _script_crashed or finalui._loop_started:
        return
    for window in finalui._open_windows:
        if window._alive:
            window.loop()
            return
