"""Shared bits every eulib widget gets."""

from .theme import get_theme

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

    _pack_opts = None

    def hide(self):
        """Take the widget off the screen (it remembers its spot settings)."""
        self.pack_forget()
        return self

    def show(self):
        """Put a hidden widget back."""
        self.pack(**(self._pack_opts or {}))
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
