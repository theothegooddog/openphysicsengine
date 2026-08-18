import tkinter as tk
from tkinter import ttk


class PartView(tk.Frame):
    def __init__(self, parent, name: str, item_type: str, depth: int, children: bool):
        super().__init__(parent)
        self.configure(bg="white")

        # Indentation based on depth
        if depth > 0:
            indent_space = ttk.Separator(self, orient="vertical")
            indent_space.pack(side=tk.LEFT, padx=(depth * 5, 5), fill=tk.Y)

        # Icon/Type representation (using text symbols as a fallback for SF Symbols)
        icon_map = {
            "globe": "🌐",
            "cube": "📦",
            "chevron.left.forwardslash.chevron.right": " </> ",
            "archivebox": "📁",
            "graph.3d": "📊",
        }
        icon_char = icon_map.get(item_type, "📄")

        icon_label = tk.Label(self, text=icon_char, bg="white", font=("Arial", 10))
        icon_label.pack(side=tk.LEFT, padx=2)

        name_label = tk.Label(self, text=name, bg="white", font=("Arial", 10))
        name_label.pack(side=tk.LEFT, padx=2)

        if children:
            chevron_label = tk.Label(
                self, text=">", bg="white", fg="gray", font=("Arial", 10)
            )
            chevron_label.pack(side=tk.LEFT, padx=5)


class ContentView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Swift to Tkinter Translation")
        self.geometry("400x300")
        self.configure(bg="white")

        self.create_widgets()

    def create_widgets(self):
        # Top toolbar simulation (HStack with gray background and squares)
        toolbar = tk.Frame(self, bg="gray", padx=5, pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        for _ in range(10):
            lbl = tk.Label(
                toolbar, text="☐", bg="gray", fg="black", font=("Arial", 12)
            )
            lbl.pack(side=tk.LEFT, padx=2)

        # Divider
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(side=tk.TOP, fill=tk.X, pady=2)

        # Main content area with Scrollbars (ScrollView equivalent)
        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for scrolling
        canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=canvas.yview
        )
        h_scrollbar = ttk.Scrollbar(
            main_frame, orient="horizontal", command=canvas.xview
        )

        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack scroll components
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate parts (VStack content)
        parts_data = [
            ("Workspace", "globe", 0, True),
            ("Part", "cube", 1, False),
            ("Code", "chevron.left.forwardslash.chevron.right", 1, False),
            ("GameStorage", "archivebox", 0, True),
            ("Missile", "cube", 1, True),
            ("Mesh", "graph.3d", 2, False),
        ]

        for name, p_type, depth, children in parts_data:
            part_widget = PartView(
                scrollable_frame,
                name=name,
                item_type=p_type,
                depth=depth,
                children=children,
            )
            part_widget.pack(anchor="w", fill=tk.X, pady=2)


def main():
    app = ContentView()
    app.mainloop()


if __name__ == "__main__":
    main()