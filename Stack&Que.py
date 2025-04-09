import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
from datetime import datetime


class StackQueueVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stack Queue Visualizer")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # App state
        self.data_structure = tk.StringVar(value="stack")
        self.elements = []
        self.animating = False
        self.highlighted_index = None
        self.history = []
        self.history_index = -1
        self.animation_speed = tk.IntVar(value=50)
        self.max_elements = tk.IntVar(value=10)
        self.theme = tk.StringVar(value="light")
        self.animation_enabled = tk.BooleanVar(value=True)
        self.operation_log = []

        # Color themes
        self.themes = {
            "light": {
                "stack": "#BFDBFE",  # bg-blue-200
                "queue": "#FBCFE8",  # bg-pink-200
                "highlight": "#FDE047",  # bg-yellow-300
                "stack_active": "#3B82F6",  # bg-blue-500
                "queue_active": "#EC4899",  # bg-pink-500
                "background": "#F3F4F6",  # bg-gray-100
                "card": "#FFFFFF",  # bg-white
                "text": "#1F2937",  # text-gray-800
                "button": "#E5E7EB",  # bg-gray-200
            },
            "dark": {
                "stack": "#1E40AF",  # bg-blue-800
                "queue": "#6B21A8",  # bg-purple-800
                "highlight": "#F59E0B",  # bg-amber-500
                "stack_active": "#2563EB",  # bg-blue-600
                "queue_active": "#9333EA",  # bg-purple-600
                "background": "#111827",  # bg-gray-900
                "card": "#1F2937",  # bg-gray-800
                "text": "#E5E7EB",  # text-gray-200
                "button": "#374151",  # bg-gray-700
            },
            "neon": {
                "stack": "#06B6D4",  # bg-cyan-500
                "queue": "#D946EF",  # bg-fuchsia-500
                "highlight": "#A3E635",  # bg-lime-400
                "stack_active": "#0891B2",  # bg-cyan-600
                "queue_active": "#C026D3",  # bg-fuchsia-600
                "background": "#000000",  # bg-black
                "card": "#111827",  # bg-gray-900
                "text": "#4ADE80",  # text-green-400
                "button": "#1F2937",  # bg-gray-800
            }
        }

        # Create UI
        self.setup_ui()

        # Initialize log
        self.add_to_log("info", f"{self.data_structure.get().capitalize()} initialized")

    def setup_ui(self):
        # Configure overall layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)  # Visualization area takes most space

        # Header frame and other UI elements...
        header_frame = tk.Frame(self.root, bg=self.themes[self.theme.get()]["background"])
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Title
        title_label = tk.Label(
            header_frame,
            text="Stack and Queue Visualizer",
            font=("Helvetica", 16, "bold"),
            bg=self.themes[self.theme.get()]["background"],
            fg=self.themes[self.theme.get()]["text"]
        )
        title_label.pack(side=tk.LEFT)

        # Data structure toggle buttons
        toggle_frame = tk.Frame(header_frame, bg=self.themes[self.theme.get()]["background"])
        toggle_frame.pack(side=tk.RIGHT, padx=10)

        stack_button = tk.Button(
            toggle_frame,
            text="Stack",
            command=lambda: self.toggle_data_structure("stack"),
            bg=self.themes[self.theme.get()]["stack_active"] if self.data_structure.get() == "stack" else self.themes[self.theme.get()]["button"],
            fg="white" if self.data_structure.get() == "stack" else self.themes[self.theme.get()]["text"],
            relief=tk.RAISED if self.data_structure.get() == "stack" else tk.FLAT
        )
        stack_button.pack(side=tk.LEFT)

        queue_button = tk.Button(
            toggle_frame,
            text="Queue",
            command=lambda: self.toggle_data_structure("queue"),
            bg=self.themes[self.theme.get()]["queue_active"] if self.data_structure.get() == "queue" else self.themes[self.theme.get()]["button"],
            fg="white" if self.data_structure.get() == "queue" else self.themes[self.theme.get()]["text"],
            relief=tk.RAISED if self.data_structure.get() == "queue" else tk.FLAT
        )
        queue_button.pack(side=tk.LEFT)

        # Settings button
        settings_button = tk.Button(
            toggle_frame,
            text="⚙️",
            command=self.toggle_settings,
            bg=self.themes[self.theme.get()]["background"],
            fg=self.themes[self.theme.get()]["text"]
        )
        settings_button.pack(side=tk.LEFT, padx=5)

        # Help button
        help_button = tk.Button(
            toggle_frame,
            text="❓",
            command=self.toggle_tutorial,
            bg=self.themes[self.theme.get()]["background"],
            fg=self.themes[self.theme.get()]["text"]
        )
        help_button.pack(side=tk.LEFT, padx=5)

        # Settings panel (initially hidden)
        self.settings_frame = tk.Frame(self.root, bg=self.themes[self.theme.get()]["card"], bd=1, relief=tk.SOLID)
        # Will be shown when settings button is clicked

        # Tutorial panel (initially hidden)
        self.tutorial_frame = tk.Frame(self.root, bg=self.themes[self.theme.get()]["card"], bd=1, relief=tk.SOLID)
        # Will be shown when help button is clicked

        # Controls frame
        controls_frame = tk.Frame(self.root, bg=self.themes[self.theme.get()]["background"])
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Input elements
        input_frame = tk.Frame(controls_frame, bg=self.themes[self.theme.get()]["background"])
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_entry = tk.Entry(
            input_frame,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            insertbackground=self.themes[self.theme.get()]["text"]
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self.add_element())

        add_button = tk.Button(
            input_frame,
            text="Push" if self.data_structure.get() == "stack" else "Enqueue",
            command=self.add_element,
            bg="#10B981",  # Green
            fg="white"
        )
        add_button.pack(side=tk.LEFT, padx=2)

        remove_button = tk.Button(
            input_frame,
            text="Pop" if self.data_structure.get() == "stack" else "Dequeue",
            command=self.remove_element,
            bg="#EF4444",  # Red
            fg="white"
        )
        remove_button.pack(side=tk.LEFT, padx=2)

        # History and utility buttons
        button_frame = tk.Frame(controls_frame, bg=self.themes[self.theme.get()]["background"])
        button_frame.pack(side=tk.RIGHT)

        undo_button = tk.Button(
            button_frame,
            text="⏪",
            command=self.undo,
            bg="#6B7280",  # Gray
            fg="white"
        )
        undo_button.pack(side=tk.LEFT, padx=2)

        redo_button = tk.Button(
            button_frame,
            text="⏩",
            command=self.redo,
            bg="#6B7280",  # Gray
            fg="white"
        )
        redo_button.pack(side=tk.LEFT, padx=2)

        reset_button = tk.Button(
            button_frame,
            text="🔄",
            command=self.reset,
            bg="#6B7280",  # Gray
            fg="white"
        )
        reset_button.pack(side=tk.LEFT, padx=2)

        randomize_button = tk.Button(
            button_frame,
            text="Randomize",
            command=self.randomize,
            bg="#8B5CF6",  # Purple
            fg="white"
        )
        randomize_button.pack(side=tk.LEFT, padx=2)

        copy_button = tk.Button(
            button_frame,
            text="Copy",
            command=self.copy_to_clipboard,
            bg="#3B82F6",  # Blue
            fg="white"
        )
        copy_button.pack(side=tk.LEFT, padx=2)

        # Visualization area
        self.viz_frame = tk.Frame(
            self.root,
            bg=self.themes[self.theme.get()]["card"],
            bd=1,
            relief=tk.SOLID
        )
        self.viz_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Canvas for drawing elements
        self.canvas = tk.Canvas(
            self.viz_frame,
            bg=self.themes[self.theme.get()]["card"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Stats and log frame
        stats_log_frame = tk.Frame(self.root, bg=self.themes[self.theme.get()]["background"])
        stats_log_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        # Stats panel
        stats_frame = tk.Frame(
            stats_log_frame,
            bg=self.themes[self.theme.get()]["card"],
            bd=1,
            relief=tk.SOLID,
            width=380,
            height=150
        )
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        stats_frame.pack_propagate(False)

        stats_title = tk.Label(
            stats_frame,
            text="Current State",
            font=("Helvetica", 10, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        )
        stats_title.pack(anchor="w", padx=10, pady=5)

        stats_content_frame = tk.Frame(stats_frame, bg=self.themes[self.theme.get()]["card"])
        stats_content_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Left side stats
        stats_left = tk.Frame(stats_content_frame, bg=self.themes[self.theme.get()]["card"])
        stats_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.structure_info_label = tk.Label(
            stats_left,
            text="Stack Properties:",
            font=("Helvetica", 9, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            anchor="w",
            justify=tk.LEFT
        )
        self.structure_info_label.pack(anchor="w")

        self.structure_stats_label = tk.Label(
            stats_left,
            text="Size: 0\nMax Size: 10",
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            anchor="w",
            justify=tk.LEFT
        )
        self.structure_stats_label.pack(anchor="w")

        # Right side stats
        stats_right = tk.Frame(stats_content_frame, bg=self.themes[self.theme.get()]["card"])
        stats_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            stats_right,
            text="Elements (0):",
            font=("Helvetica", 9, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            anchor="w"
        ).pack(anchor="w")

        self.elements_display = tk.Text(
            stats_right,
            height=3,
            width=30,
            bg=self.themes[self.theme.get()]["background"],
            fg=self.themes[self.theme.get()]["text"],
            font=("Courier", 9)
        )
        self.elements_display.pack(fill=tk.BOTH, expand=True)
        self.elements_display.insert(tk.END, "Empty stack")
        self.elements_display.config(state=tk.DISABLED)

        # Log panel
        log_frame = tk.Frame(
            stats_log_frame,
            bg=self.themes[self.theme.get()]["card"],
            bd=1,
            relief=tk.SOLID,
            width=380,
            height=150
        )
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        log_frame.pack_propagate(False)

        tk.Label(
            log_frame,
            text="Operation Log",
            font=("Helvetica", 10, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(anchor="w", padx=10, pady=5)

        log_container = tk.Frame(log_frame, bg=self.themes[self.theme.get()]["card"])
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_display = tk.Text(
            log_container,
            height=6,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            wrap=tk.WORD
        )
        self.log_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scrollbar = tk.Scrollbar(log_container, command=self.log_display.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_display.config(yscrollcommand=log_scrollbar.set)
        self.log_display.config(state=tk.DISABLED)

        # Set up the text tags for log coloring
        self.log_display.tag_configure("add", foreground="#10B981")  # Green
        self.log_display.tag_configure("remove", foreground="#EF4444")  # Red
        self.log_display.tag_configure("error", foreground="#F59E0B")  # Yellow/Amber
        self.log_display.tag_configure("info", foreground="#3B82F6")  # Blue

        # Now that canvas and other elements exist, apply the theme
        self.apply_theme()

        # Update UI
        self.update_ui()

    def toggle_settings(self):
        # Check if settings frame exists and is mapped
        if hasattr(self, "settings_frame") and self.settings_frame.winfo_ismapped():
            self.settings_frame.grid_forget()
            return

        # Create settings frame if not already done
        if hasattr(self, "settings_frame"):
            self.settings_frame.destroy()

        self.settings_frame = tk.Frame(
            self.root,
            bg=self.themes[self.theme.get()]["card"],
            bd=1,
            relief=tk.SOLID
        )
        self.settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Settings header
        header_frame = tk.Frame(self.settings_frame, bg=self.themes[self.theme.get()]["card"])
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            header_frame,
            text="Settings",
            font=("Helvetica", 10, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(side=tk.LEFT)

        close_button = tk.Button(
            header_frame,
            text="✕",
            command=lambda: self.settings_frame.grid_forget(),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            bd=0
        )
        close_button.pack(side=tk.RIGHT)

        # Settings content
        settings_content = tk.Frame(self.settings_frame, bg=self.themes[self.theme.get()]["card"])
        settings_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Theme selection
        theme_frame = tk.Frame(settings_content, bg=self.themes[self.theme.get()]["card"])
        theme_frame.grid(row=0, column=0, sticky="w", pady=5)

        tk.Label(
            theme_frame,
            text="Theme",
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(side=tk.LEFT)

        theme_options = ttk.Combobox(
            theme_frame,
            textvariable=self.theme,
            values=["light", "dark", "neon"],
            state="readonly",
            width=10
        )
        theme_options.pack(side=tk.LEFT, padx=5)
        theme_options.bind("<<ComboboxSelected>>", lambda e: self.apply_theme())

        # Max elements
        max_elements_frame = tk.Frame(settings_content, bg=self.themes[self.theme.get()]["card"])
        max_elements_frame.grid(row=0, column=1, sticky="w", pady=5, padx=10)

        tk.Label(
            max_elements_frame,
            text=f"Max Elements ({self.max_elements.get()})",
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(side=tk.LEFT)

        max_scale = tk.Scale(
            max_elements_frame,
            from_=5,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.max_elements,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            highlightthickness=0
        )
        max_scale.pack(side=tk.LEFT)

        # Animation speed
        speed_frame = tk.Frame(settings_content, bg=self.themes[self.theme.get()]["card"])
        speed_frame.grid(row=1, column=0, sticky="w", pady=5)

        tk.Label(
            speed_frame,
            text="Animation Speed",
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(side=tk.LEFT)

        speed_scale = tk.Scale(
            speed_frame,
            from_=10,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.animation_speed,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            highlightthickness=0
        )
        speed_scale.pack(side=tk.LEFT)

        # Animation toggle
        animation_frame = tk.Frame(settings_content, bg=self.themes[self.theme.get()]["card"])
        animation_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        animation_check = tk.Checkbutton(
            animation_frame,
            text="Enable Animations",
            variable=self.animation_enabled,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            selectcolor=self.themes[self.theme.get()]["card"],
            activebackground=self.themes[self.theme.get()]["card"],
            activeforeground=self.themes[self.theme.get()]["text"]
        )
        animation_check.pack(side=tk.LEFT)

    def toggle_tutorial(self):
        # Check if tutorial frame exists and is mapped
        if hasattr(self, "tutorial_frame") and self.tutorial_frame.winfo_ismapped():
            self.tutorial_frame.grid_forget()
            return

        # Create tutorial frame if not already done
        if hasattr(self, "tutorial_frame"):
            self.tutorial_frame.destroy()

        self.tutorial_frame = tk.Frame(
            self.root,
            bg=self.themes[self.theme.get()]["card"],
            bd=1,
            relief=tk.SOLID
        )
        self.tutorial_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Tutorial header
        header_frame = tk.Frame(self.tutorial_frame, bg=self.themes[self.theme.get()]["card"])
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            header_frame,
            text="How to Use",
            font=("Helvetica", 10, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(side=tk.LEFT)

        close_button = tk.Button(
            header_frame,
            text="✕",
            command=lambda: self.tutorial_frame.grid_forget(),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"],
            bd=0
        )
        close_button.pack(side=tk.RIGHT)

        # Tutorial content
        tutorial_content = tk.Frame(self.tutorial_frame, bg=self.themes[self.theme.get()]["card"])
        tutorial_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Stack info
        stack_frame = tk.Frame(tutorial_content, bg=self.themes[self.theme.get()]["card"])
        stack_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        tk.Label(
            stack_frame,
            text="Stack (LIFO)",
            font=("Helvetica", 9, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(anchor="w")

        stack_info = tk.Label(
            stack_frame,
            text="• Push: Add element to the top\n• Pop: Remove element from the top\n• Last In, First Out principle",
            justify=tk.LEFT,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        )
        stack_info.pack(anchor="w", padx=5)

        # Queue info
        queue_frame = tk.Frame(tutorial_content, bg=self.themes[self.theme.get()]["card"])
        queue_frame.grid(row=0, column=1, sticky="nw", padx=5, pady=5)

        tk.Label(
            queue_frame,
            text="Queue (FIFO)",
            font=("Helvetica", 9, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(anchor="w")

        queue_info = tk.Label(
            queue_frame,
            text="• Enqueue: Add element to the back\n• Dequeue: Remove element from the front\n• First In, First Out principle",
            justify=tk.LEFT,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        )
        queue_info.pack(anchor="w", padx=5)

        # Features info
        features_frame = tk.Frame(tutorial_content, bg=self.themes[self.theme.get()]["card"])
        features_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(
            features_frame,
            text="Features",
            font=("Helvetica", 9, "bold"),
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        ).pack(anchor="w")

        features_info = tk.Label(
            features_frame,
            text="• Undo/Redo: Navigate through operation history\n• Copy: Copy elements to clipboard\n• Settings: Change theme, animation speed, and maximum elements\n• Operation Log: Track actions performed",
            justify=tk.LEFT,
            bg=self.themes[self.theme.get()]["card"],
            fg=self.themes[self.theme.get()]["text"]
        )
        features_info.pack(anchor="w", padx=5)

    def apply_theme(self):
        self.current_theme = self.themes[self.theme.get()]

        # Update the root background
        self.root.config(bg=self.current_theme["background"])

        # We'd need to update all UI elements with the new theme
        # This would require reconfiguring all widgets
        # For simplicity, we'll just notify that a restart is needed
        self.update_ui()

    def update_ui(self):
        # Update element labels
        ds_type = self.data_structure.get()
        if hasattr(self, 'structure_info_label'):
            self.structure_info_label.config(text=f"{ds_type.capitalize()} Properties:")

        # Update stats
        if hasattr(self, 'structure_stats_label'):
            stats_text = f"Size: {len(self.elements)}\n"
            if self.elements and ds_type == "stack":
                stats_text += f"Top: \"{self.elements[-1]}\"\n"
            elif self.elements and ds_type == "queue":
                stats_text += f"Front: \"{self.elements[0]}\"\n"
                stats_text += f"Back: \"{self.elements[-1]}\"\n"
            stats_text += f"Max Size: {self.max_elements.get()}"
            self.structure_stats_label.config(text=stats_text)

        # Update elements display
        if hasattr(self, 'elements_display'):
            self.elements_display.config(state=tk.NORMAL)
            self.elements_display.delete(1.0, tk.END)
            if self.elements:
                self.elements_display.insert(tk.END, f"[{', '.join(self.elements)}]")
            else:
                self.elements_display.insert(tk.END, f"Empty {ds_type}")
            self.elements_display.config(state=tk.DISABLED)

        # Update visualization
        self.render_visualization()

    def render_visualization(self):
        self.canvas.delete("all")

        if not self.elements:
            # Show empty state
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text=f"Empty {self.data_structure.get()}\n  ",
                font=("Helvetica", 12),
                fill=self.current_theme["text"],
                justify=tk.CENTER
            )
            return

        ds_type = self.data_structure.get()

        if ds_type == "stack":
            # Stack visualization (vertical)
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                30,
                text="Top ▲",
                font=("Helvetica", 10, "bold"),
                fill=self.current_theme["text"]
            )

            element_width = 120
            element_height = 40

            # Calculate positions
            center_x = self.canvas.winfo_width() // 2
            start_y = self.canvas.winfo_height() - 50  # Start from bottom

            for i, element in enumerate(self.elements):
                y_pos = start_y - i * (element_height + 10)

                # Background color based on highlight
                bg_color = self.current_theme["highlight"] if i == self.highlighted_index else self.current_theme["stack"]

                self.canvas.create_rectangle(
                    center_x - element_width // 2,
                    y_pos - element_height // 2,
                    center_x + element_width // 2,
                    y_pos + element_height // 2,
                    fill=bg_color,
                    outline="#6B7280",
                    width=2,
                    tags=f"element-{i}"
                )

                self.canvas.create_text(
                    center_x,
                    y_pos,
                    text=element,
                    font=("Helvetica", 10, "bold"),
                    fill=self.current_theme["text"]
                )

                self.canvas.create_text(
                    center_x - element_width // 2 + 10,
                    y_pos - element_height // 2 + 10,
                    text=str(len(self.elements) - 1 - i),
                    font=("Helvetica", 8),
                    fill=self.current_theme["text"],
                    anchor=tk.NW
                )

            # Show "Bottom" text below the stack
            if self.elements:
                self.canvas.create_text(
                    center_x,
                    start_y + 30,
                    text="Bottom",
                    font=("Helvetica", 10),
                    fill=self.current_theme["text"]
                )
        else:
            # Queue visualization (horizontal)
            self.canvas.create_text(
                50,
                30,
                text="◀ Front",
                font=("Helvetica", 10, "bold"),
                fill=self.current_theme["text"],
                anchor=tk.W
            )

            self.canvas.create_text(
                self.canvas.winfo_width() - 50,
                30,
                text="Back ▶",
                font=("Helvetica", 10, "bold"),
                fill=self.current_theme["text"],
                anchor=tk.E
            )

            element_width = 80
            element_height = 40

            # Calculate positions
            center_y = self.canvas.winfo_height() // 2
            start_x = 50

            for i, element in enumerate(self.elements):
                x_pos = start_x + i * (element_width + 10)

                # Background color based on highlight
                bg_color = self.current_theme["highlight"] if i == self.highlighted_index else self.current_theme["queue"]

                self.canvas.create_rectangle(
                    x_pos,
                    center_y - element_height // 2,
                    x_pos + element_width,
                    center_y + element_height // 2,
                    fill=bg_color,
                    outline="#6B7280",
                    width=2,
                    tags=f"element-{i}"
                )

                self.canvas.create_text(
                    x_pos + element_width // 2,
                    center_y,
                    text=element,
                    font=("Helvetica", 10, "bold"),
                    fill=self.current_theme["text"]
                )

                self.canvas.create_text(
                    x_pos + 5,
                    center_y - element_height // 2 + 10,
                    text=str(i),
                    font=("Helvetica", 8),
                    fill=self.current_theme["text"],
                    anchor=tk.NW
                )

    # Move these methods to the class level (fix indentation)
    def add_to_log(self, tag, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.operation_log.append((tag, log_entry))

        self.log_display.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, log_entry + "\n", tag)
        self.log_display.see(tk.END)
        self.log_display.config(state=tk.DISABLED)

    def toggle_data_structure(self, ds_type):
        if ds_type != self.data_structure.get():
            self.data_structure.set(ds_type)
            self.add_to_log("info", f"Switched to {ds_type}")
            self.update_ui()

    def add_element(self):
        if self.animating:
            return

        value = self.input_entry.get().strip()
        if not value:
            self.add_to_log("error", "Cannot add empty element")
            return

        if len(self.elements) >= self.max_elements.get():
            self.add_to_log("error", f"Maximum capacity ({self.max_elements.get()}) reached")
            return

        self.animating = True
        ds_type = self.data_structure.get()

        # Save state for undo
        self.history = self.history[:self.history_index + 1]
        self.history.append(("add", value, list(self.elements)))
        self.history_index += 1

        self.elements.append(value)
        self.input_entry.delete(0, tk.END)

        operation = "Pushed" if ds_type == "stack" else "Enqueued"
        self.add_to_log("add", f"{operation} '{value}'")

        if self.animation_enabled.get():
            self.highlighted_index = len(self.elements) - 1
            self.update_ui()
            self.root.after(self.animation_speed.get() * 10, self.finish_animation)
        else:
            self.animating = False
            self.update_ui()

    def remove_element(self):
        if self.animating or not self.elements:
            if not self.elements:
                self.add_to_log("error", f"Empty {self.data_structure.get()}")
            return

        self.animating = True
        ds_type = self.data_structure.get()

        # Save state for undo
        self.history = self.history[:self.history_index + 1]
        removed_value = self.elements[-1] if ds_type == "stack" else self.elements[0]
        self.history.append(("remove", removed_value, list(self.elements)))
        self.history_index += 1

        self.highlighted_index = len(self.elements) - 1 if ds_type == "stack" else 0

        if ds_type == "stack":
            self.elements.pop()
            operation = "Popped"
        else:
            self.elements.pop(0)
            operation = "Dequeued"

        self.add_to_log("remove", f"{operation} '{removed_value}'")

        if self.animation_enabled.get():
            self.update_ui()
            self.root.after(self.animation_speed.get() * 10, self.finish_animation)
        else:
            self.animating = False
            self.update_ui()

    def finish_animation(self):
        self.highlighted_index = None
        self.animating = False
        self.update_ui()

    def undo(self):
        if self.animating or self.history_index < 0:
            return

        operation, value, prev_state = self.history[self.history_index]
        self.history_index -= 1

        self.elements = list(prev_state)
        ds_type = self.data_structure.get()

        if operation == "add":
            self.add_to_log("info", f"Undo: Removed '{value}'")
        else:
            self.add_to_log("info", f"Undo: Restored '{value}'")

        self.update_ui()

    def redo(self):
        if self.animating or self.history_index >= len(self.history) - 1:
            return

        self.history_index += 1
        operation, value, _ = self.history[self.history_index]

        ds_type = self.data_structure.get()
        if operation == "add":
            self.elements.append(value)
            self.add_to_log("info", f"Redo: Added '{value}'")
        else:
            self.elements.pop(-1 if ds_type == "stack" else 0)
            self.add_to_log("info", f"Redo: Removed '{value}'")

        self.update_ui()

    def reset(self):
        if self.animating:
            return

        self.elements.clear()
        self.history.clear()
        self.history_index = -1
        self.add_to_log("info", f"{self.data_structure.get().capitalize()} reset")
        self.update_ui()

    def randomize(self):
        if self.animating:
            return

        self.elements.clear()
        length = random.randint(1, self.max_elements.get())
        self.elements = [''.join(random.choices(string.ascii_letters + string.digits, k=5))
                         for _ in range(length)]

        self.history = self.history[:self.history_index + 1]
        self.history.append(("randomize", None, []))
        self.history_index += 1

        self.add_to_log("info", f"Randomized with {length} elements")
        self.update_ui()

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps(self.elements))
        self.add_to_log("info", "Elements copied to clipboard")


if __name__ == "__main__":
    root = tk.Tk()
    app = StackQueueVisualizer(root)
    root.mainloop()


