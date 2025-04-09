import sys
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QSlider, QLabel,
                             QComboBox, QGroupBox, QRadioButton, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from collections import deque


class GraphVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Algorithm Visualizer")
        self.setMinimumSize(1000, 700)

        # Algorithm state variables
        self.graph = nx.Graph()
        self.pos = {}  # Node positions
        self.current_step = 0
        self.algorithm_steps = []  # Will store states for stepping through
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_forward)
        self.animation_speed = 500  # ms between steps

        # Algorithm variables
        self.algorithm = "DFS"  # Default algorithm
        self.start_node = 0
        self.visited = set()
        self.queue_or_stack = []  # Will be used as queue for BFS or stack for DFS
        self.path = []  # Track the path taken

        # Set up the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create top control panel
        self.create_control_panel()

        # Create visualization area
        self.create_visualization_area()

        # Create bottom info panel
        self.create_info_panel()

        # Initial graph generation
        self.generate_random_graph()

    def create_control_panel(self):
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Node control
        nodes_label = QLabel("Number of Nodes:")
        self.nodes_spinner = QSpinBox()
        self.nodes_spinner.setRange(5, 20)
        self.nodes_spinner.setValue(10)
        self.nodes_spinner.valueChanged.connect(self.generate_random_graph)

        # Edge density control
        density_label = QLabel("Edge Density:")
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setRange(1, 10)
        self.density_slider.setValue(4)
        self.density_slider.valueChanged.connect(self.generate_random_graph)

        # Algorithm selection
        algo_label = QLabel("Algorithm:")
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["DFS", "BFS"])
        self.algo_combo.currentTextChanged.connect(self.set_algorithm)

        # Start node selection
        start_node_label = QLabel("Start Node:")
        self.start_node_spinner = QSpinBox()
        self.start_node_spinner.setRange(0, 9)
        self.start_node_spinner.setValue(0)

        # Speed control
        speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.update_speed)

        # Add widgets to control layout
        control_layout.addWidget(nodes_label)
        control_layout.addWidget(self.nodes_spinner)
        control_layout.addWidget(density_label)
        control_layout.addWidget(self.density_slider)
        control_layout.addWidget(algo_label)
        control_layout.addWidget(self.algo_combo)
        control_layout.addWidget(start_node_label)
        control_layout.addWidget(self.start_node_spinner)
        control_layout.addWidget(speed_label)
        control_layout.addWidget(self.speed_slider)

        self.main_layout.addWidget(control_panel)

    def create_visualization_area(self):
        # Create matplotlib figure
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)

        # Create step label
        self.step_label = QLabel("Step 0")
        self.step_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.step_label)

    def create_info_panel(self):
        info_panel = QWidget()
        info_layout = QHBoxLayout(info_panel)

        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.step_backward)
        self.prev_button.setEnabled(False)

        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step_forward)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_animation)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_animation)
        self.stop_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_visualization)

        self.new_graph_button = QPushButton("New Graph")
        self.new_graph_button.clicked.connect(self.generate_random_graph)

        # Add buttons to info layout
        info_layout.addWidget(self.prev_button)
        info_layout.addWidget(self.step_button)
        info_layout.addWidget(self.start_button)
        info_layout.addWidget(self.stop_button)
        info_layout.addWidget(self.reset_button)
        info_layout.addWidget(self.new_graph_button)

        # Status display
        self.status_label = QLabel("Ready")
        info_layout.addWidget(self.status_label)

        self.main_layout.addWidget(info_panel)

        # Algorithm details panel
        details_panel = QWidget()
        details_layout = QHBoxLayout(details_panel)

        # Queue/Stack visualization
        queue_group = QGroupBox("Queue/Stack")
        queue_layout = QVBoxLayout(queue_group)
        self.queue_label = QLabel("Empty")
        queue_layout.addWidget(self.queue_label)

        # Visited nodes
        visited_group = QGroupBox("Visited Nodes")
        visited_layout = QVBoxLayout(visited_group)
        self.visited_label = QLabel("None")
        visited_layout.addWidget(self.visited_label)

        # Current state
        state_group = QGroupBox("Current State")
        state_layout = QVBoxLayout(state_group)
        self.state_label = QLabel("Not started")
        state_layout.addWidget(self.state_label)

        details_layout.addWidget(queue_group)
        details_layout.addWidget(visited_group)
        details_layout.addWidget(state_group)

        self.main_layout.addWidget(details_panel)

    def generate_random_graph(self):
        num_nodes = self.nodes_spinner.value()
        density = self.density_slider.value() / 10.0  # Convert to float between 0.1 and 1.0

        # Update start node spinner range
        self.start_node_spinner.setRange(0, num_nodes - 1)

        # Generate new graph
        self.graph = nx.gnp_random_graph(num_nodes, density)

        # Ensure graph is connected
        while not nx.is_connected(self.graph):
            # Add edges until connected
            components = list(nx.connected_components(self.graph))
            if len(components) > 1:
                # Connect two random nodes from different components
                comp1 = random.choice(list(components[0]))
                comp2 = random.choice(list(components[1]))
                self.graph.add_edge(comp1, comp2)

        # Calculate positions for nodes
        self.pos = nx.spring_layout(self.graph)

        # Reset visualization
        self.reset_visualization()

        # Draw initial graph
        self.draw_graph()

    def draw_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Draw edges
        nx.draw_networkx_edges(self.graph, self.pos, ax=ax, edge_color='gray')

        # Initialize node colors
        node_colors = []
        for node in self.graph.nodes():
            if node in self.visited:
                if node == self.current_node if hasattr(self, 'current_node') else False:
                    node_colors.append('red')  # Current node
                else:
                    node_colors.append('green')  # Visited node
            elif hasattr(self, 'queue_or_stack') and node in self.queue_or_stack:
                node_colors.append('orange')  # In queue/stack
            else:
                node_colors.append('skyblue')  # Unvisited node

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, self.pos, ax=ax, node_color=node_colors,
                               node_size=500)

        # Draw node labels
        nx.draw_networkx_labels(self.graph, self.pos, ax=ax, font_color='black')

        # Create legend labels and handles
        labels = ["Unvisited", "In Queue/Stack", "Visited", "Current"]
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in ['skyblue', 'orange', 'green', 'red']]

        # Add legend
        ax.legend(handles, labels, loc='upper right', bbox_to_anchor=(1, 1),
                  fontsize=10, framealpha=0.7)

        # Update title with algorithm information
        ax.set_title(f"{self.algorithm} - Step {self.current_step}")

        # Remove axis
        ax.axis('off')

        # Update canvas
        self.canvas.draw()

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.reset_visualization()

    def update_speed(self):
        # Convert slider value (1-10) to ms (1000-100)
        self.animation_speed = 1100 - (self.speed_slider.value() * 100)

    def calculate_algorithm_steps(self):
        self.algorithm_steps = []
        self.visited = set()
        start_node = self.start_node_spinner.value()

        if self.algorithm == "DFS":
            # DFS implementation
            self.queue_or_stack = [start_node]  # Using as stack

            while self.queue_or_stack:
                current_node = self.queue_or_stack[-1]  # Peek at top of stack

                # Save the current state
                self.algorithm_steps.append({
                    'visited': self.visited.copy(),
                    'queue_or_stack': self.queue_or_stack.copy(),
                    'current_node': current_node,
                    'action': 'exploring' if current_node not in self.visited else 'backtracking'
                })

                if current_node not in self.visited:
                    self.visited.add(current_node)

                    # Get unvisited neighbors
                    neighbors = sorted([n for n in self.graph.neighbors(current_node)
                                        if n not in self.visited], reverse=True)

                    # If no unvisited neighbors, backtrack (pop)
                    if not neighbors:
                        self.queue_or_stack.pop()
                    else:
                        # Add neighbors to stack (in reverse order so they come out in order)
                        for neighbor in neighbors:
                            self.queue_or_stack.append(neighbor)
                else:
                    # Already visited this node, backtrack
                    self.queue_or_stack.pop()

        else:  # BFS
            # BFS implementation
            self.queue_or_stack = deque([start_node])  # Using as queue
            self.visited.add(start_node)

            # Save initial state
            self.algorithm_steps.append({
                'visited': self.visited.copy(),
                'queue_or_stack': list(self.queue_or_stack),
                'current_node': start_node,
                'action': 'start'
            })

            while self.queue_or_stack:
                current_node = self.queue_or_stack.popleft()

                # Save the current state (after popping)
                self.algorithm_steps.append({
                    'visited': self.visited.copy(),
                    'queue_or_stack': list(self.queue_or_stack),
                    'current_node': current_node,
                    'action': 'exploring'
                })

                # Get all neighbors
                neighbors = sorted([n for n in self.graph.neighbors(current_node)
                                    if n not in self.visited])

                for neighbor in neighbors:
                    if neighbor not in self.visited:
                        self.queue_or_stack.append(neighbor)
                        self.visited.add(neighbor)

                        # Save state after each neighbor is added to queue and visited
                        self.algorithm_steps.append({
                            'visited': self.visited.copy(),
                            'queue_or_stack': list(self.queue_or_stack),
                            'current_node': current_node,
                            'action': f'added {neighbor} to queue'
                        })

    def start_animation(self):
        self.timer.start(self.animation_speed)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Running...")

    def stop_animation(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Paused")

    def step_forward(self):
        if self.current_step == 0:
            # Initialize the algorithm steps if this is the first step
            self.calculate_algorithm_steps()

        if self.current_step < len(self.algorithm_steps):
            # Get current state
            state = self.algorithm_steps[self.current_step]
            self.visited = state['visited']
            self.queue_or_stack = state['queue_or_stack']
            self.current_node = state['current_node']

            # Update UI
            self.draw_graph()
            self.update_info_labels(state)

            # Increment step counter
            self.current_step += 1
            self.step_label.setText(f"Step {self.current_step}")

            # Enable previous button if we're past step 0
            self.prev_button.setEnabled(self.current_step > 0)

            # Check if we've reached the end
            if self.current_step >= len(self.algorithm_steps):
                self.stop_animation()
                self.status_label.setText("Completed")
        else:
            self.stop_animation()
            self.status_label.setText("Completed")

    def step_backward(self):
        if self.current_step > 0:
            # Decrement step counter
            self.current_step -= 1

            # If at beginning, reset
            if self.current_step == 0:
                self.reset_visualization()
                return

            # Get previous state
            state = self.algorithm_steps[self.current_step - 1]
            self.visited = state['visited']
            self.queue_or_stack = state['queue_or_stack']
            self.current_node = state['current_node']

            # Update UI
            self.draw_graph()
            self.update_info_labels(state)
            self.step_label.setText(f"Step {self.current_step}")

            # Disable previous button if we're at step 0
            self.prev_button.setEnabled(self.current_step > 0)

            # Update status
            self.status_label.setText("Stepped back")

    def reset_visualization(self):
        # Stop any running animation
        self.timer.stop()

        # Reset algorithm state
        self.current_step = 0
        self.visited = set()
        self.queue_or_stack = []
        if hasattr(self, 'current_node'):
            del self.current_node

        # Reset UI
        self.draw_graph()
        self.step_label.setText("Step 0")
        self.prev_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Ready")

        # Reset info labels
        self.queue_label.setText("Empty")
        self.visited_label.setText("None")
        self.state_label.setText("Not started")

    def update_info_labels(self, state):
        # Update queue/stack label
        if not state['queue_or_stack']:
            self.queue_label.setText("Empty")
        else:
            queue_str = ' → '.join(str(node) for node in state['queue_or_stack'])
            self.queue_label.setText(queue_str)

        # Update visited label
        if not state['visited']:
            self.visited_label.setText("None")
        else:
            visited_str = ', '.join(str(node) for node in sorted(state['visited']))
            self.visited_label.setText(visited_str)

        # Update state label
        self.state_label.setText(f"Node: {state['current_node']}, Action: {state['action']}")


def main():
    app = QApplication(sys.argv)
    window = GraphVisualizerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()