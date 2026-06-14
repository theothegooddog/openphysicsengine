r"""
  ___  ____  _____   _    _   _   _ _   _  ____ _   _ _____ ____
 / _ \|  _ \| ____| | |  | | | | | | \ | |/ ___| | | | ____|  _ \
| | | | |_) |  _|   | |  | | | | | |  \| | |   | |_| |  _| | |_) |
| |_| |  __/| |___  | |__| |_| | |\  | |___|  _  | |___|  _ <
 \___/|_|   |_____| |_____\___/|_| \_|\____|_| |_|_____|_| \_\

Open-Physics launcher.

A small GUI front-end for the engine. Pick a mode, hit Launch, and it
starts the right process for you:

  * Single Player  ->  python main.py
  * Multiplayer    ->  python main.py --server <addr> --name <you>
  * Host Server    ->  python server.py --host <iface> --port <port>

Run:  python launcher.py
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

HERE = os.path.dirname(os.path.abspath(__file__))

# GitHub-dark-ish palette so it matches the engine window.
BG = "#0d1117"
PANEL = "#161b22"
FG = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#238636"
GREEN_HI = "#2ea043"
BORDER = "#30363d"

LOGO = r"""  ___  ____  _____
 / _ \|  _ \| ____|
| | | | |_) |  _|
| |_| |  __/| |___
 \___/|_|   |_____|  OPEN-PHYSICS"""


class Launcher:

	def __init__(self, root):
		self.root = root
		root.title("Open-Physics Launcher")
		root.configure(bg=BG)
		root.resizable(False, False)

		self.mode = tk.StringVar(value="single")
		self.server = tk.StringVar(value="127.0.0.1:5555")
		self.name = tk.StringVar(value="player")
		self.host = tk.StringVar(value="0.0.0.0")
		self.port = tk.StringVar(value="5555")

		self._build()
		self._sync_fields()

	### widget helpers ###

	def _label(self, parent, text, **kw):
		opts = dict(bg=BG, fg=MUTED, font=("Courier", 11))
		opts.update(kw)
		return tk.Label(parent, text=text, **opts)

	def _entry(self, parent, var):
		return tk.Entry(
		 parent, textvariable=var, bg=PANEL, fg=FG, font=("Courier", 11),
		 insertbackground=FG, relief="flat", highlightthickness=1,
		 highlightbackground=BORDER, highlightcolor=ACCENT, width=24,
		)

	def _radio(self, parent, text, value):
		return tk.Radiobutton(
		 parent, text=text, value=value, variable=self.mode,
		 command=self._sync_fields, bg=BG, fg=FG, font=("Courier", 11),
		 selectcolor=PANEL, activebackground=BG, activeforeground=ACCENT,
		 anchor="w",
		)

	### layout ###

	def _build(self):
		pad = 18

		tk.Label(
		 self.root, text=LOGO, bg=BG, fg=ACCENT,
		 font=("Courier", 11, "bold"), justify="left",
		).grid(row=0, column=0, columnspan=2, sticky="w", padx=pad, pady=(pad, 8))

		self._label(
		 self.root, "an open-source physics engine", fg=MUTED,
		).grid(row=1, column=0, columnspan=2, sticky="w", padx=pad, pady=(0, pad))

		# mode picker
		modes = tk.Frame(self.root, bg=BG)
		modes.grid(row=2, column=0, columnspan=2, sticky="we", padx=pad)
		self._label(modes, "MODE", fg=ACCENT, font=("Courier", 10, "bold")).pack(anchor="w")
		self._radio(modes, "Single Player", "single").pack(fill="x")
		self._radio(modes, "Multiplayer (join a server)", "multi").pack(fill="x")
		self._radio(modes, "Host Server", "host").pack(fill="x")

		# options
		opts = tk.Frame(self.root, bg=BG)
		opts.grid(row=3, column=0, columnspan=2, sticky="we", padx=pad, pady=(pad, 0))

		self.name_lbl = self._label(opts, "Player name")
		self.name_lbl.grid(row=0, column=0, sticky="w", pady=4)
		self.name_ent = self._entry(opts, self.name)
		self.name_ent.grid(row=0, column=1, sticky="we", pady=4)

		self.server_lbl = self._label(opts, "Server address")
		self.server_lbl.grid(row=1, column=0, sticky="w", pady=4)
		self.server_ent = self._entry(opts, self.server)
		self.server_ent.grid(row=1, column=1, sticky="we", pady=4)

		self.host_lbl = self._label(opts, "Bind host")
		self.host_lbl.grid(row=2, column=0, sticky="w", pady=4)
		self.host_ent = self._entry(opts, self.host)
		self.host_ent.grid(row=2, column=1, sticky="we", pady=4)

		self.port_lbl = self._label(opts, "Port")
		self.port_lbl.grid(row=3, column=0, sticky="w", pady=4)
		self.port_ent = self._entry(opts, self.port)
		self.port_ent.grid(row=3, column=1, sticky="we", pady=4)

		# launch button
		self.launch_btn = tk.Button(
		 self.root, text="LAUNCH", command=self._launch,
		 bg=GREEN, fg="white", activebackground=GREEN_HI,
		 activeforeground="white", font=("Courier", 12, "bold"),
		 relief="flat", padx=12, pady=8, cursor="hand2",
		)
		self.launch_btn.grid(row=4, column=0, columnspan=2, sticky="we",
		                     padx=pad, pady=pad)

		self.status = self._label(self.root, "", fg=MUTED)
		self.status.grid(row=5, column=0, columnspan=2, sticky="w",
		                 padx=pad, pady=(0, pad))

	def _set_row(self, lbl, ent, on):
		state = "normal" if on else "disabled"
		ent.configure(state=state)
		lbl.configure(fg=MUTED if on else BORDER)

	def _sync_fields(self):
		mode = self.mode.get()
		self._set_row(self.name_lbl, self.name_ent, mode == "multi")
		self._set_row(self.server_lbl, self.server_ent, mode == "multi")
		self._set_row(self.host_lbl, self.host_ent, mode == "host")
		self._set_row(self.port_lbl, self.port_ent, mode == "host")

	### actions ###

	def _spawn(self, args):
		"""Launch a sibling script as its own process."""
		try:
			subprocess.Popen([sys.executable] + args, cwd=HERE)
			return True
		except OSError as e:
			messagebox.showerror("Launch failed", str(e))
			return False

	def _launch(self):
		mode = self.mode.get()
		if mode == "single":
			ok = self._spawn([os.path.join(HERE, "main.py")])
			self._flash("Launched single-player window" if ok else "")
		elif mode == "multi":
			server = self.server.get().strip()
			name = self.name.get().strip()
			if not server:
				messagebox.showwarning("Missing server", "Enter a server address.")
				return
			args = [os.path.join(HERE, "main.py"), "--server", server]
			if name:
				args += ["--name", name]
			ok = self._spawn(args)
			self._flash(f"Connecting to {server}" if ok else "")
		elif mode == "host":
			port = self.port.get().strip() or "5555"
			if not port.isdigit():
				messagebox.showwarning("Bad port", "Port must be a number.")
				return
			args = [os.path.join(HERE, "server.py"),
			        "--host", self.host.get().strip() or "0.0.0.0",
			        "--port", port]
			ok = self._spawn(args)
			self._flash(f"Server hosting on port {port}" if ok else "")

	def _flash(self, text):
		self.status.configure(text=text)


def main():
	root = tk.Tk()
	Launcher(root)
	root.mainloop()


if __name__ == "__main__":
	main()
