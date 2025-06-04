import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import random
import time

class AnimatedMSTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated MST Algorithms: Prim's vs Kruskal's")
        self.root.geometry("1400x900")
        
        # Initialize graph
        self.graph = nx.Graph()
        self.pos = {}
        
        # Animation state
        self.animation_steps = []
        self.current_step = 0
        self.is_animating = False
        self.animation = None
        self.animation_speed = 1000  # milliseconds
        
        # Setup UI
        self.setup_ui()
        
        # Generate initial random graph
        self.generate_random_graph()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Top row buttons
        top_buttons = ttk.Frame(control_frame)
        top_buttons.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        ttk.Button(top_buttons, text="Generate Random Graph", 
                  command=self.generate_random_graph).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(top_buttons, text="Animate Prim's", 
                  command=self.animate_prims).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(top_buttons, text="Animate Kruskal's", 
                  command=self.animate_kruskals).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(top_buttons, text="Stop Animation", 
                  command=self.stop_animation).grid(row=0, column=3, padx=(0, 10))
        
        # Animation controls
        anim_controls = ttk.Frame(control_frame)
        anim_controls.grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Label(anim_controls, text="Speed:").grid(row=0, column=0, padx=(0, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(anim_controls, from_=0.2, to=3.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=150, command=self.update_speed)
        speed_scale.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Button(anim_controls, text="Previous Step", 
                  command=self.prev_step).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(anim_controls, text="Next Step", 
                  command=self.next_step).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(anim_controls, text="Reset", 
                  command=self.reset_animation).grid(row=0, column=4)
        
        # Graph parameters
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Label(param_frame, text="Nodes:").grid(row=0, column=0)
        self.nodes_var = tk.StringVar(value="8")
        ttk.Entry(param_frame, textvariable=self.nodes_var, width=5).grid(row=0, column=1, padx=(5, 15))
        
        ttk.Label(param_frame, text="Edge Probability:").grid(row=0, column=2)
        self.prob_var = tk.StringVar(value="0.4")
        ttk.Entry(param_frame, textvariable=self.prob_var, width=5).grid(row=0, column=3, padx=(5, 0))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 8))
        self.fig.suptitle("Animated Minimum Spanning Tree Algorithm")
        
        # Canvas for matplotlib
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status and info frame
        info_frame = ttk.LabelFrame(main_frame, text="Algorithm Status", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Current step info
        step_frame = ttk.Frame(info_frame)
        step_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.step_label = ttk.Label(step_frame, text="Step: 0/0", font=("TkDefaultFont", 12, "bold"))
        self.step_label.grid(row=0, column=0, sticky=tk.W)
        
        self.algorithm_label = ttk.Label(step_frame, text="Algorithm: None", font=("TkDefaultFont", 10))
        self.algorithm_label.grid(row=1, column=0, sticky=tk.W)
        
        # Step description
        self.step_text = tk.Text(info_frame, height=4, width=80, wrap=tk.WORD)
        step_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.step_text.yview)
        self.step_text.configure(yscrollcommand=step_scrollbar.set)
        
        self.step_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        step_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
    
    def generate_random_graph(self):
        try:
            n_nodes = int(self.nodes_var.get())
            prob = float(self.prob_var.get())
            
            if n_nodes < 3 or n_nodes > 15:
                messagebox.showerror("Error", "Number of nodes must be between 3 and 15")
                return
            
            if prob < 0 or prob > 1:
                messagebox.showerror("Error", "Edge probability must be between 0 and 1")
                return
            
            self.stop_animation()
            
            # Generate random graph
            self.graph = nx.erdos_renyi_graph(n_nodes, prob)
            
            # Ensure graph is connected
            if not nx.is_connected(self.graph):
                components = list(nx.connected_components(self.graph))
                for i in range(len(components) - 1):
                    node1 = random.choice(list(components[i]))
                    node2 = random.choice(list(components[i + 1]))
                    self.graph.add_edge(node1, node2)
            
            # Add random weights to edges
            for u, v in self.graph.edges():
                self.graph[u][v]['weight'] = random.randint(1, 20)
            
            # Generate positions for consistent layout
            self.pos = nx.spring_layout(self.graph, seed=42, k=2, iterations=50)
            
            # Reset animation
            self.animation_steps = []
            self.current_step = 0
            
            # Update display
            self.draw_graph()
            self.update_status("Graph generated", f"{n_nodes} nodes, {len(self.graph.edges())} edges")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def animate_prims(self):
        if len(self.graph.nodes()) == 0:
            messagebox.showwarning("Warning", "Please generate a graph first")
            return
        
        self.stop_animation()
        self.prepare_prims_animation()
        self.start_animation("Prim's Algorithm")
    
    def animate_kruskals(self):
        if len(self.graph.nodes()) == 0:
            messagebox.showwarning("Warning", "Please generate a graph first")
            return
        
        self.stop_animation()
        self.prepare_kruskals_animation()
        self.start_animation("Kruskal's Algorithm")
    
    def prepare_prims_animation(self):
        # Prim's algorithm step-by-step
        self.animation_steps = []
        visited = set()
        mst_edges = []
        
        # Initial state
        self.animation_steps.append({
            'type': 'initial',
            'visited': set(),
            'mst_edges': [],
            'current_edge': None,
            'description': "Starting Prim's Algorithm. We'll grow the MST by adding the minimum weight edge from visited nodes.",
            'total_weight': 0
        })
        
        # Start from node 0
        start_node = list(self.graph.nodes())[0]
        visited.add(start_node)
        total_weight = 0
        
        self.animation_steps.append({
            'type': 'start',
            'visited': visited.copy(),
            'mst_edges': mst_edges.copy(),
            'current_edge': None,
            'description': f"Step 1: Start with node {start_node}. Mark it as visited (green).",
            'total_weight': total_weight
        })
        
        step_count = 2
        while len(visited) < len(self.graph.nodes()):
            # Find minimum weight edge
            min_edge = None
            min_weight = float('inf')
            candidate_edges = []
            
            for node in visited:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        weight = self.graph[node][neighbor]['weight']
                        candidate_edges.append((node, neighbor, weight))
                        if weight < min_weight:
                            min_weight = weight
                            min_edge = (node, neighbor)
            
            # Show candidate edges
            if candidate_edges:
                self.animation_steps.append({
                    'type': 'candidates',
                    'visited': visited.copy(),
                    'mst_edges': mst_edges.copy(),
                    'candidate_edges': candidate_edges,
                    'current_edge': min_edge,
                    'description': f"Step {step_count}a: Consider all edges from visited nodes to unvisited nodes. Candidates: {[(u, v, w) for u, v, w in candidate_edges]}. Minimum is {min_edge} with weight {min_weight}.",
                    'total_weight': total_weight
                })
            
            if min_edge:
                mst_edges.append(min_edge)
                visited.add(min_edge[1])
                total_weight += min_weight
                
                self.animation_steps.append({
                    'type': 'add_edge',
                    'visited': visited.copy(),
                    'mst_edges': mst_edges.copy(),
                    'current_edge': min_edge,
                    'description': f"Step {step_count}b: Add edge {min_edge} with weight {min_weight} to MST. Mark node {min_edge[1]} as visited. Total weight: {total_weight}",
                    'total_weight': total_weight
                })
                step_count += 1
        
        # Final state
        self.animation_steps.append({
            'type': 'complete',
            'visited': visited.copy(),
            'mst_edges': mst_edges.copy(),
            'current_edge': None,
            'description': f"Prim's Algorithm Complete! MST has {len(mst_edges)} edges with total weight {total_weight}.",
            'total_weight': total_weight
        })
    
    def prepare_kruskals_animation(self):
        # Kruskal's algorithm step-by-step
        self.animation_steps = []
        
        # Union-Find class
        class UnionFind:
            def __init__(self, nodes):
                self.parent = {node: node for node in nodes}
                self.rank = {node: 0 for node in nodes}
            
            def find(self, x):
                if self.parent[x] != x:
                    self.parent[x] = self.find(self.parent[x])
                return self.parent[x]
            
            def union(self, x, y):
                px, py = self.find(x), self.find(y)
                if px == py:
                    return False
                if self.rank[px] < self.rank[py]:
                    px, py = py, px
                self.parent[py] = px
                if self.rank[px] == self.rank[py]:
                    self.rank[px] += 1
                return True
            
            def get_components(self):
                components = {}
                for node in self.parent:
                    root = self.find(node)
                    if root not in components:
                        components[root] = []
                    components[root].append(node)
                return list(components.values())
        
        # Get all edges sorted by weight
        edges = [(u, v, data['weight']) for u, v, data in self.graph.edges(data=True)]
        edges.sort(key=lambda x: x[2])
        
        # Initial state
        self.animation_steps.append({
            'type': 'initial',
            'mst_edges': [],
            'current_edge': None,
            'components': [[node] for node in self.graph.nodes()],
            'description': f"Starting Kruskal's Algorithm. Sort all edges by weight: {[(u, v, w) for u, v, w in edges]}",
            'total_weight': 0
        })
        
        uf = UnionFind(self.graph.nodes())
        mst_edges = []
        total_weight = 0
        step_count = 1
        
        for u, v, weight in edges:
            # Show current edge being considered
            self.animation_steps.append({
                'type': 'consider',
                'mst_edges': mst_edges.copy(),
                'current_edge': (u, v),
                'components': uf.get_components(),
                'description': f"Step {step_count}: Consider edge ({u}, {v}) with weight {weight}. Check if it creates a cycle.",
                'total_weight': total_weight
            })
            
            if uf.union(u, v):
                mst_edges.append((u, v))
                total_weight += weight
                
                self.animation_steps.append({
                    'type': 'add_edge',
                    'mst_edges': mst_edges.copy(),
                    'current_edge': (u, v),
                    'components': uf.get_components(),
                    'description': f"Step {step_count}: Add edge ({u}, {v}) with weight {weight}. No cycle created. Total weight: {total_weight}",
                    'total_weight': total_weight
                })
                
                if len(mst_edges) == len(self.graph.nodes()) - 1:
                    break
            else:
                self.animation_steps.append({
                    'type': 'reject',
                    'mst_edges': mst_edges.copy(),
                    'current_edge': (u, v),
                    'components': uf.get_components(),
                    'description': f"Step {step_count}: Reject edge ({u}, {v}) - would create a cycle!",
                    'total_weight': total_weight
                })
            
            step_count += 1
        
        # Final state
        self.animation_steps.append({
            'type': 'complete',
            'mst_edges': mst_edges.copy(),
            'current_edge': None,
            'components': [list(self.graph.nodes())],
            'description': f"Kruskal's Algorithm Complete! MST has {len(mst_edges)} edges with total weight {total_weight}.",
            'total_weight': total_weight
        })
    
    def start_animation(self, algorithm_name):
        if not self.animation_steps:
            return
        
        self.is_animating = True
        self.current_step = 0
        self.algorithm_name = algorithm_name
        self.algorithm_label.config(text=f"Algorithm: {algorithm_name}")
        
        self.animate_step()
    
    def animate_step(self):
        if not self.is_animating or self.current_step >= len(self.animation_steps):
            self.is_animating = False
            return
        
        self.draw_current_step()
        self.current_step += 1
        
        if self.current_step < len(self.animation_steps):
            # Calculate delay based on speed
            delay = int(self.animation_speed / self.speed_var.get())
            self.root.after(delay, self.animate_step)
        else:
            self.is_animating = False
    
    def draw_current_step(self):
        if not self.animation_steps or self.current_step >= len(self.animation_steps):
            return
        
        step = self.animation_steps[self.current_step]
        self.ax.clear()
        
        # Update status
        self.step_label.config(text=f"Step: {self.current_step + 1}/{len(self.animation_steps)}")
        self.step_text.delete(1.0, tk.END)
        self.step_text.insert(tk.END, step['description'])
        
        if len(self.graph.nodes()) == 0:
            return
        
        # Choose colors and drawing based on algorithm
        if hasattr(self, 'algorithm_name') and 'Prim' in self.algorithm_name:
            self.draw_prims_step(step)
        else:
            self.draw_kruskals_step(step)
        
        self.ax.set_title(f"{getattr(self, 'algorithm_name', 'MST Algorithm')} - Total Weight: {step['total_weight']}")
        self.ax.axis('off')
        self.canvas.draw()
    
    def draw_prims_step(self, step):
        # Draw all edges in light gray
        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, alpha=0.2, edge_color='lightgray')
        
        # Color nodes based on visited status
        node_colors = []
        for node in self.graph.nodes():
            if node in step.get('visited', set()):
                node_colors.append('lightgreen')
            else:
                node_colors.append('lightblue')
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax, node_color=node_colors, 
                              node_size=700, alpha=0.8)
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax, font_size=12, font_weight='bold')
        
        # Draw MST edges in red
        if step['mst_edges']:
            nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, edgelist=step['mst_edges'], 
                                  edge_color='red', width=3)
        
        # Highlight current edge being considered
        if step.get('current_edge'):
            nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, 
                                  edgelist=[step['current_edge']], 
                                  edge_color='orange', width=4, alpha=0.8)
        
        # Highlight candidate edges
        if step.get('candidate_edges'):
            candidate_edge_list = [(u, v) for u, v, w in step['candidate_edges']]
            nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, 
                                  edgelist=candidate_edge_list, 
                                  edge_color='yellow', width=2, alpha=0.6)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, ax=self.ax, font_size=10)
    
    def draw_kruskals_step(self, step):
        # Draw all edges in light gray
        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, alpha=0.2, edge_color='lightgray')
        
        # Color nodes based on components
        if step.get('components'):
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 
                     'lightcyan', 'wheat', 'lavender', 'mistyrose', 'honeydew']
            node_colors = {}
            for i, component in enumerate(step['components']):
                color = colors[i % len(colors)]
                for node in component:
                    node_colors[node] = color
            
            node_color_list = [node_colors.get(node, 'lightgray') for node in self.graph.nodes()]
        else:
            node_color_list = ['lightblue'] * len(self.graph.nodes())
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax, node_color=node_color_list, 
                              node_size=700, alpha=0.8)
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax, font_size=12, font_weight='bold')
        
        # Draw MST edges in red
        if step['mst_edges']:
            nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, edgelist=step['mst_edges'], 
                                  edge_color='red', width=3)
        
        # Highlight current edge
        if step.get('current_edge'):
            color = 'orange' if step['type'] == 'consider' else ('green' if step['type'] == 'add_edge' else 'red')
            width = 4 if step['type'] in ['consider', 'add_edge'] else 3
            nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, 
                                  edgelist=[step['current_edge']], 
                                  edge_color=color, width=width, alpha=0.8)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, ax=self.ax, font_size=10)
    
    def draw_graph(self):
        self.ax.clear()
        if len(self.graph.nodes()) == 0:
            return
        
        # Draw basic graph
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax, node_color='lightblue', 
                              node_size=700, alpha=0.8)
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax, font_size=12, font_weight='bold')
        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, alpha=0.6)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, ax=self.ax, font_size=10)
        
        self.ax.set_title("Graph - Ready for Algorithm")
        self.ax.axis('off')
        self.canvas.draw()
    
    def stop_animation(self):
        self.is_animating = False
        if self.animation:
            self.animation.event_source.stop()
    
    def reset_animation(self):
        self.stop_animation()
        self.current_step = 0
        if self.animation_steps:
            self.draw_current_step()
        else:
            self.draw_graph()
        self.update_status("Animation reset", "Ready to start")
    
    def next_step(self):
        if self.animation_steps and self.current_step < len(self.animation_steps) - 1:
            self.current_step += 1
            self.draw_current_step()
    
    def prev_step(self):
        if self.animation_steps and self.current_step > 0:
            self.current_step -= 1
            self.draw_current_step()
    
    def update_speed(self, value):
        # Speed is updated in real-time during animation
        pass
    
    def update_status(self, status, details=""):
        self.step_text.delete(1.0, tk.END)
        self.step_text.insert(tk.END, f"{status}\n{details}")
        self.step_label.config(text="Step: 0/0")
        self.algorithm_label.config(text="Algorithm: None")

def main():
    root = tk.Tk()
    app = AnimatedMSTVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()