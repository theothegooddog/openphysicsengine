"""Shared bits every eulib widget gets."""

import tkinter as tk

from .theme import get_theme


def raise_widget(widget):
    """Raise a widget in the stacking order. (Canvas.lift() is taken —
    tkinter aliases it to tag_raise, which works on canvas items — so we
    always go through Misc.lift.)"""
    tk.Misc.lift(widget)


def raise_tree(widget):
    """Raise a widget AND everything laid out inside it, keeping layers in
    order. Needed because a widget moved into a sibling container (pack/place
    with in_=...) only shows if it sits above that container in the stacking
    order."""
    raise_widget(widget)
    for child in widget.pack_slaves() + widget.place_slaves():
        raise_tree(child)

# keyword args that control layout instead of the widget itself
PACK_KEYS = ("side", "fill", "expand", "anchor", "pad", "padx", "pady")


def take_pack(opts):
    """Pull the layout-related kwargs out of a factory call's options."""
    return {k: opts.pop(k) for k in PACK_KEYS if k in opts}


def parent_bg(parent):
    """Background color of a container (so labels/checkboxes blend in)."""
    try:
        return parent.cget("background")
    except Exception:
        return get_theme(parent)["bg"]


def font(size=11, bold=False):
    return ("Helvetica", int(size), "bold" if bold else "normal")


class EasyWidget:
    """Mixin: every eulib widget can hide/show/enable/disable itself."""

    _geo = None                # ("pack" | "place", options) — how it was laid out
    _layout_defaults = {}      # how this kind of widget likes to be packed

    def hide(self):
        """Take the widget off the screen (it remembers its spot)."""
        manager = self.winfo_manager()
        if manager == "place":
            self.place_forget()
        elif manager == "grid":
            self.grid_forget()
        else:
            self.pack_forget()
        return self

    def show(self):
        """Put a hidden widget back where it was."""
        if self._geo:
            kind, opts = self._geo
            if kind == "place":
                self.place(**opts)
            else:
                self.pack(**opts)
            raise_tree(self)
        else:
            self.pack()
        return self

    def disable(self):
        try:
            self.configure(state="disabled")
        except Exception:
            pass
        return self

    def enable(self):
        try:
            self.configure(state="normal")
        except Exception:
            pass
        return self
