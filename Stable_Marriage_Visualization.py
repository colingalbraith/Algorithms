import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import random
import tkinter as tk
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import copy


class StableMarriageVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stable Marriage Algorithm Visualizer")
        self.root.geometry("1200x800")

        # Default parameters
        self.n_participants = 5
        self.men = [f"M{i + 1}" for i in range(self.n_participants)]
        self.women = [f"W{i + 1}" for i in range(self.n_participants)]

        # Algorithm state variables
        self.reset_algorithm()

        # Set up the main UI
        self.setup_ui()
        self.initialize_preferences()

        # Animation settings
        self.animation_speed = 1000  # ms between frames
        self.animation_running = False
        self.anim = None

    def reset_algorithm(self):
        """Reset the algorithm state"""
        self.free_men = self.men.copy()
        self.proposals = {m: 0 for m in self.men}
        self.engagements = {w: None for w in self.women}
        self.current_proposals = []  # Current proposals for visualization
        self.step = 0
        self.algorithm_done = False

        # History of states for the previous button
        self.history = []
        self.save_state()  # Save initial state

    def save_state(self):
        """Save the current state for history navigation"""
        state = {
            'free_men': self.free_men.copy(),
            'proposals': copy.deepcopy(self.proposals),
            'engagements': copy.deepcopy(self.engagements),
            'current_proposals': self.current_proposals.copy(),
            'step': self.step,
            'algorithm_done': self.algorithm_done,
            'status': self.status_var.get() if hasattr(self, 'status_var') else "Ready"
        }
        self.history.append(state)

    def initialize_preferences(self):
        """Generate random preferences"""
        # Create random preferences
        self.men_prefs = {m: random.sample(self.women, len(self.women)) for m in self.men}
        self.women_prefs = {w: random.sample(self.men, len(self.men)) for w in self.women}

        # Create rankings for quick lookup
        self.women_rankings = {w: {m: i for i, m in enumerate(prefs)} for w, prefs in self.women_prefs.items()}

        # Update preference displays
        self.update_preference_display()

    def setup_ui(self):
        """Set up the UI components"""
        # Create frames
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.left_panel = ttk.Frame(self.content_frame, padding="10")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.content_frame, padding="10")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Set up visualization
        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Setup controls
        self.setup_controls()
        self.setup_preferences_display()

        # Create the graph
        self.G = nx.Graph()
        self.update_graph()

    def setup_controls(self):
        """Set up the control buttons and sliders"""
        # Number of participants slider
        ttk.Label(self.control_frame, text="Number of Participants:").pack(side=tk.LEFT, padx=5)
        self.participants_var = tk.IntVar(value=self.n_participants)
        self.participant_slider = ttk.Scale(
            self.control_frame,
            from_=3, to=10,
            orient=tk.HORIZONTAL,
            variable=self.participants_var,
            command=self.on_participants_change
        )
        self.participant_slider.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.control_frame, textvariable=self.participants_var).pack(side=tk.LEFT)

        # Speed control
        ttk.Label(self.control_frame, text="Speed:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.IntVar(value=5)  # 1-10 scale
        self.speed_slider = ttk.Scale(
            self.control_frame,
            from_=1, to=10,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.on_speed_change
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Animation control buttons
        self.btn_frame = ttk.Frame(self.control_frame)
        self.btn_frame.pack(side=tk.RIGHT, padx=10)

        self.previous_btn = ttk.Button(self.btn_frame, text="Previous", command=self.previous_step)
        self.previous_btn.pack(side=tk.LEFT, padx=2)

        self.step_btn = ttk.Button(self.btn_frame, text="Step", command=self.step_animation)
        self.step_btn.pack(side=tk.LEFT, padx=2)

        self.start_btn = ttk.Button(self.btn_frame, text="Start", command=self.start_animation)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = ttk.Button(self.btn_frame, text="Stop", command=self.stop_animation)
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = ttk.Button(self.btn_frame, text="Reset", command=self.reset_animation)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        self.randomize_btn = ttk.Button(self.btn_frame, text="Randomize Preferences",
                                        command=self.initialize_preferences)
        self.randomize_btn.pack(side=tk.LEFT, padx=2)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.control_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=10)

    def setup_preferences_display(self):
        """Set up the preferences display panel"""
        # Notebook for preferences and results
        self.pref_notebook = ttk.Notebook(self.right_panel)
        self.pref_notebook.pack(fill=tk.BOTH, expand=True)

        # Men's preferences tab
        self.men_pref_frame = ttk.Frame(self.pref_notebook, padding="10")
        self.pref_notebook.add(self.men_pref_frame, text="Men's Preferences")

        # Women's preferences tab
        self.women_pref_frame = ttk.Frame(self.pref_notebook, padding="10")
        self.pref_notebook.add(self.women_pref_frame, text="Women's Preferences")

        # Current state tab
        self.state_frame = ttk.Frame(self.pref_notebook, padding="10")
        self.pref_notebook.add(self.state_frame, text="Current State")

        # Men's preferences text area
        self.men_pref_text = scrolledtext.ScrolledText(self.men_pref_frame, width=30, height=20)
        self.men_pref_text.pack(fill=tk.BOTH, expand=True)

        # Women's preferences text area
        self.women_pref_text = scrolledtext.ScrolledText(self.women_pref_frame, width=30, height=20)
        self.women_pref_text.pack(fill=tk.BOTH, expand=True)

        # Current state text area
        self.state_text = scrolledtext.ScrolledText(self.state_frame, width=30, height=20)
        self.state_text.pack(fill=tk.BOTH, expand=True)

    def update_preference_display(self):
        """Update the preference displays with current preferences"""
        # Update men's preferences
        self.men_pref_text.delete(1.0, tk.END)
        for man, prefs in self.men_prefs.items():
            self.men_pref_text.insert(tk.END, f"{man}: {' > '.join(prefs)}\n")

        # Update women's preferences
        self.women_pref_text.delete(1.0, tk.END)
        for woman, prefs in self.women_prefs.items():
            self.women_pref_text.insert(tk.END, f"{woman}: {' > '.join(prefs)}\n")

    def update_state_display(self):
        """Update the current state display"""
        self.state_text.delete(1.0, tk.END)

        # Show current step
        self.state_text.insert(tk.END, f"Step: {self.step}\n\n")

        # Show free men
        self.state_text.insert(tk.END, "Free Men:\n")
        if self.free_men:
            self.state_text.insert(tk.END, ", ".join(self.free_men) + "\n\n")
        else:
            self.state_text.insert(tk.END, "None\n\n")

        # Show current proposals
        self.state_text.insert(tk.END, "Current Proposals:\n")
        if self.current_proposals:
            for m, w in self.current_proposals:
                self.state_text.insert(tk.END, f"{m} → {w}\n")
        else:
            self.state_text.insert(tk.END, "None\n")
        self.state_text.insert(tk.END, "\n")

        # Show engagements
        self.state_text.insert(tk.END, "Current Engagements:\n")
        for woman, man in self.engagements.items():
            if man:
                self.state_text.insert(tk.END, f"{man} ❤️ {woman}\n")

        # Show if algorithm is done
        if self.algorithm_done:
            self.state_text.insert(tk.END, "\nAlgorithm has completed! Stable matching found.\n")

    def on_participants_change(self, event):
        """Handler for when number of participants changes"""
        new_n = self.participants_var.get()
        if new_n != self.n_participants:
            self.n_participants = new_n
            self.men = [f"M{i + 1}" for i in range(self.n_participants)]
            self.women = [f"W{i + 1}" for i in range(self.n_participants)]
            self.reset_algorithm()
            self.initialize_preferences()
            self.update_graph()
            self.draw_graph()

    def on_speed_change(self, event):
        """Handler for when speed slider changes"""
        # Convert 1-10 scale to milliseconds (1000ms to 100ms)
        self.animation_speed = int(1100 - (self.speed_var.get() * 100))

        # Update animation if running
        if self.animation_running and self.anim:
            self.anim.event_source.interval = self.animation_speed

    def update_graph(self):
        """Update the graph structure when participants change"""
        self.G.clear()
        self.G.add_nodes_from(self.men, bipartite=0)
        self.G.add_nodes_from(self.women, bipartite=1)

        # Calculate node positions
        self.pos = {}
        men_y = np.linspace(0, 1, len(self.men))
        women_y = np.linspace(0, 1, len(self.women))

        for i, m in enumerate(self.men):
            self.pos[m] = (0.3, men_y[i])

        for i, w in enumerate(self.women):
            self.pos[w] = (0.7, women_y[i])

    def draw_graph(self):
        """Draw the current state of the graph"""
        self.ax.clear()

        # Draw nodes
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.men, node_color='skyblue',
                               node_size=700, ax=self.ax)
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.women, node_color='lightpink',
                               node_size=700, ax=self.ax)

        # Draw labels
        nx.draw_networkx_labels(self.G, self.pos, font_size=12, ax=self.ax)

        # Draw current proposals (red dashed)
        if self.current_proposals:
            nx.draw_networkx_edges(self.G, self.pos, edgelist=self.current_proposals,
                                   edge_color='red', style='dashed', width=2, ax=self.ax,
                                   arrows=True, arrowstyle='->', arrowsize=15)

        # Draw engagements (blue solid)
        engaged_edges = [(m, w) for w, m in self.engagements.items() if m]
        if engaged_edges:
            nx.draw_networkx_edges(self.G, self.pos, edgelist=engaged_edges,
                                   edge_color='blue', style='solid', width=2, ax=self.ax)

        # Formatting
        self.ax.set_title(f"Stable Marriage Algorithm - Step {self.step}")
        self.ax.set_axis_off()
        self.ax.set_xlim(-0.1, 1.1)
        self.ax.set_ylim(-0.1, 1.1)

        # Update canvas
        self.canvas.draw()

    def gale_shapley_step(self):
        """Perform one step of the Gale-Shapley algorithm"""
        if self.algorithm_done or not self.free_men:
            self.algorithm_done = True
            self.status_var.set("Algorithm complete!")
            return False

        # Save the current state before proceeding
        self.save_state()

        self.step += 1
        self.current_proposals = []

        # Get a free man
        m = self.free_men.pop(0)

        # Get his next preference
        if self.proposals[m] >= len(self.women):
            # This man has exhausted his preferences (shouldn't happen in standard algorithm)
            self.status_var.set(f"Warning: {m} has exhausted all preferences!")
            return True

        w = self.men_prefs[m][self.proposals[m]]
        self.proposals[m] += 1

        # Add this proposal to current proposals for visualization
        self.current_proposals.append((m, w))

        # Check if woman is already engaged
        current = self.engagements[w]
        if current is None:
            # Woman is free, accept proposal
            self.engagements[w] = m
            self.status_var.set(f"{m} proposes to {w} and is accepted")
        else:
            # Woman must choose between current and new proposal
            if self.women_rankings[w][m] < self.women_rankings[w][current]:
                # New man is preferred
                self.engagements[w] = m
                self.free_men.append(current)
                self.status_var.set(f"{m} proposes to {w} and replaces {current}")
            else:
                # Current engagement is preferred
                self.free_men.append(m)
                self.status_var.set(f"{m} proposes to {w} but is rejected (she prefers {current})")

        # Update the state display
        self.update_state_display()

        return True

    def previous_step(self):
        """Go back to the previous step of the algorithm"""
        if self.step <= 0 or len(self.history) <= 1:
            self.status_var.set("Already at the beginning!")
            return

        # Remove the current state from history
        self.history.pop()

        # Load the previous state (which is now the last one in history)
        previous_state = self.history[-1]

        # Restore state
        self.free_men = previous_state['free_men']
        self.proposals = previous_state['proposals']
        self.engagements = previous_state['engagements']
        self.current_proposals = previous_state['current_proposals']
        self.step = previous_state['step']
        self.algorithm_done = previous_state['algorithm_done']
        self.status_var.set(f"Went back to step {self.step}")

        # Update displays
        self.update_state_display()
        self.draw_graph()

    def step_animation(self):
        """Perform a single step of the algorithm"""
        if not self.algorithm_done:
            self.gale_shapley_step()
            self.draw_graph()
        else:
            self.status_var.set("Algorithm already complete!")

    def animate(self, i):
        """Animation function for FuncAnimation"""
        if self.animation_running and not self.algorithm_done:
            if self.gale_shapley_step():
                self.draw_graph()
            else:
                self.stop_animation()
        return []

    def start_animation(self):
        """Start the animation"""
        if self.algorithm_done:
            self.status_var.set("Algorithm already complete! Reset to start again.")
            return

        self.animation_running = True

        if self.anim is None:
            self.anim = animation.FuncAnimation(
                self.fig, self.animate, interval=self.animation_speed,
                blit=True, repeat=False)
        else:
            self.anim.event_source.start()

    def stop_animation(self):
        """Stop the animation"""
        self.animation_running = False
        if self.anim:
            self.anim.event_source.stop()

    def reset_animation(self):
        """Reset the animation to the beginning"""
        # Stop animation if running
        self.stop_animation()

        # Reset algorithm state
        self.reset_algorithm()

        # Update displays
        self.update_state_display()
        self.draw_graph()
        self.status_var.set("Reset complete")

    def run(self):
        """Run the application"""
        # Initial drawing
        self.draw_graph()
        self.update_state_display()

        # Start main loop
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = StableMarriageVisualizer(root)
    app.run()