import sys
import random
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QSlider, QSpinBox, QGroupBox,
                             QRadioButton, QFrame, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.animation as animation
import numpy as np


class SortingCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(SortingCanvas, self).__init__(self.fig)
        self.setParent(parent)

        self.array = []
        self.states = []
        self.current_state_index = -1
        self.highlighted_indices = []
        self.sorted_indices = []
        self.pivot_indices = []
        self.comparison_count = 0
        self.swap_count = 0

        # Colors
        self.default_color = '#3498db'
        self.highlight_color = '#e74c3c'
        self.sorted_color = '#2ecc71'
        self.pivot_color = '#f39c12'

    def setup_array(self, size, min_val=5, max_val=100):
        self.array = [random.randint(min_val, max_val) for _ in range(size)]
        self.states = [(self.array.copy(), [], [], [], 0, 0)]  # Initial state
        self.current_state_index = 0
        self.highlighted_indices = []
        self.sorted_indices = []
        self.pivot_indices = []
        self.comparison_count = 0
        self.swap_count = 0
        self.plot_state()
        return self.array.copy()

    def custom_array(self, custom_values):
        try:
            self.array = [int(x.strip()) for x in custom_values.split(',')]
            self.states = [(self.array.copy(), [], [], [], 0, 0)]  # Initial state
            self.current_state_index = 0
            self.highlighted_indices = []
            self.sorted_indices = []
            self.pivot_indices = []
            self.comparison_count = 0
            self.swap_count = 0
            self.plot_state()
            return self.array.copy()
        except ValueError:
            return None

    def plot_state(self):
        if not self.array or self.current_state_index < 0:
            return

        self.ax.clear()

        # Load current state
        state = self.states[self.current_state_index]
        array = state[0]
        highlighted = state[1]
        sorted_indices = state[2]
        pivot_indices = state[3]

        # Create color array
        colors = [self.default_color] * len(array)

        # Apply colors based on state
        for i in sorted_indices:
            colors[i] = self.sorted_color

        for i in highlighted:
            colors[i] = self.highlight_color

        for i in pivot_indices:
            colors[i] = self.pivot_color

        # Create the bar plot
        bars = self.ax.bar(range(len(array)), array, color=colors, edgecolor='black', linewidth=0.5)

        # Add value labels on top of bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                         f'{array[i]}', ha='center', va='bottom', fontsize=8)

        # Configure the plot
        self.ax.set_xlim(-0.5, len(array) - 0.5)
        self.ax.set_ylim(0, max(array) * 1.15)
        self.ax.set_xticks(range(len(array)))
        self.ax.set_xticklabels([str(i) for i in range(len(array))], fontsize=8)
        self.ax.set_xlabel('Index')
        self.ax.set_ylabel('Value')
        self.ax.set_title(f'Sorting Visualization (Step {self.current_state_index}/{len(self.states) - 1})')

        # Add a legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.default_color, edgecolor='black', label='Unsorted'),
            Patch(facecolor=self.highlight_color, edgecolor='black', label='Comparing/Swapping'),
            Patch(facecolor=self.sorted_color, edgecolor='black', label='Sorted'),
            Patch(facecolor=self.pivot_color, edgecolor='black', label='Pivot')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', fontsize='small')

        self.fig.tight_layout()
        self.draw()

    def add_state(self, array, highlighted=None, sorted_indices=None, pivot_indices=None):
        if highlighted is None:
            highlighted = []
        if sorted_indices is None:
            sorted_indices = []
        if pivot_indices is None:
            pivot_indices = []

        self.states.append((array.copy(), highlighted.copy(), sorted_indices.copy(),
                            pivot_indices.copy(), self.comparison_count, self.swap_count))

    def go_to_state(self, index):
        if 0 <= index < len(self.states):
            self.current_state_index = index
            state = self.states[index]
            self.array = state[0]
            self.highlighted_indices = state[1]
            self.sorted_indices = state[2]
            self.pivot_indices = state[3]
            self.comparison_count = state[4]
            self.swap_count = state[5]
            self.plot_state()
            return True
        return False

    def next_state(self):
        return self.go_to_state(self.current_state_index + 1)

    def prev_state(self):
        return self.go_to_state(self.current_state_index - 1)

    def reset(self):
        return self.go_to_state(0)

    def last_state(self):
        return self.go_to_state(len(self.states) - 1)


class SortingVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sorting Algorithm Visualizer")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Sorting canvas
        self.canvas = SortingCanvas(self.central_widget, width=12, height=6)

        # Algorithm controls
        self.create_algorithm_controls()

        # Array controls
        self.create_array_controls()

        # Animation controls
        self.create_animation_controls()

        # Status panel
        self.create_status_panel()

        # Add widgets to layout
        self.main_layout.addWidget(self.algorithm_group)
        self.main_layout.addWidget(self.array_group)

        # Create splitter for canvas and status
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.canvas)
        self.splitter.addWidget(self.status_panel)
        self.splitter.setSizes([600, 200])

        self.main_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.animation_group)

        # Initialize variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_forward)
        self.speed = 500  # milliseconds
        self.current_algorithm = None

        # Generate initial array
        self.generate_array()

    def create_algorithm_controls(self):
        self.algorithm_group = QGroupBox("Algorithm Selection")
        layout = QHBoxLayout()

        self.algo_label = QLabel("Algorithm:")
        layout.addWidget(self.algo_label)

        self.algo_combo = QComboBox()
        self.algo_combo.addItems([
            "Bubble Sort",
            "Selection Sort",
            "Insertion Sort",
            "Quick Sort",
            "Merge Sort"
        ])
        layout.addWidget(self.algo_combo)

        self.order_label = QLabel("Order:")
        layout.addWidget(self.order_label)

        self.order_asc = QRadioButton("Ascending")
        self.order_asc.setChecked(True)
        layout.addWidget(self.order_asc)

        self.order_desc = QRadioButton("Descending")
        layout.addWidget(self.order_desc)

        self.start_btn = QPushButton("Sort")
        self.start_btn.clicked.connect(self.start_sorting)
        layout.addWidget(self.start_btn)

        layout.addStretch()

        self.algorithm_group.setLayout(layout)

    def create_array_controls(self):
        self.array_group = QGroupBox("Array Controls")
        layout = QHBoxLayout()

        self.size_label = QLabel("Array Size:")
        layout.addWidget(self.size_label)

        self.size_input = QSpinBox()
        self.size_input.setMinimum(5)
        self.size_input.setMaximum(100)
        self.size_input.setValue(20)
        layout.addWidget(self.size_input)

        self.generate_btn = QPushButton("Generate Random Array")
        self.generate_btn.clicked.connect(self.generate_array)
        layout.addWidget(self.generate_btn)

        self.custom_label = QLabel("Custom Array (comma-separated):")
        layout.addWidget(self.custom_label)

        self.custom_input = QComboBox()
        self.custom_input.setEditable(True)
        self.custom_input.addItems(["5, 2, 9, 1, 5, 6", "10, 9, 8, 7, 6, 5, 4, 3, 2, 1"])
        layout.addWidget(self.custom_input)

        self.apply_custom_btn = QPushButton("Apply")
        self.apply_custom_btn.clicked.connect(self.apply_custom_array)
        layout.addWidget(self.apply_custom_btn)

        layout.addStretch()

        self.array_group.setLayout(layout)

    def create_animation_controls(self):
        self.animation_group = QGroupBox("Animation Controls")
        layout = QHBoxLayout()

        self.first_btn = QPushButton("⏮ First")
        self.first_btn.clicked.connect(self.go_to_first)
        layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.step_backward)
        layout.addWidget(self.prev_btn)

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_animation)
        layout.addWidget(self.play_btn)

        self.next_btn = QPushButton("▶ Next")
        self.next_btn.clicked.connect(self.step_forward)
        layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("⏭ Last")
        self.last_btn.clicked.connect(self.go_to_last)
        layout.addWidget(self.last_btn)

        self.speed_label = QLabel("Speed:")
        layout.addWidget(self.speed_label)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(500)
        self.speed_slider.setInvertedAppearance(True)
        self.speed_slider.valueChanged.connect(self.update_speed)
        layout.addWidget(self.speed_slider)

        layout.addStretch()

        self.animation_group.setLayout(layout)

    def create_status_panel(self):
        self.status_panel = QGroupBox("Algorithm Status")
        layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        self.status_panel.setLayout(layout)

    def generate_array(self):
        size = self.size_input.value()
        self.stop_animation()
        array = self.canvas.setup_array(size)
        self.update_status("Generated new random array")
        self.update_buttons_state()

    def apply_custom_array(self):
        self.stop_animation()
        custom_input = self.custom_input.currentText()
        array = self.canvas.custom_array(custom_input)
        if array:
            self.update_status(f"Applied custom array: {custom_input}")
        else:
            self.update_status("Invalid input. Please enter comma-separated integers.")
        self.update_buttons_state()

    def update_speed(self):
        self.speed = self.speed_slider.value()
        if self.timer.isActive():
            self.timer.setInterval(self.speed)

    def toggle_animation(self):
        if self.timer.isActive():
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self):
        self.timer.start(self.speed)
        self.play_btn.setText("⏸ Pause")

    def stop_animation(self):
        self.timer.stop()
        self.play_btn.setText("▶ Play")

    def step_forward(self):
        if not self.canvas.next_state():
            self.stop_animation()
        self.update_status_from_current_state()
        self.update_buttons_state()

    def step_backward(self):
        self.stop_animation()
        self.canvas.prev_state()
        self.update_status_from_current_state()
        self.update_buttons_state()

    def go_to_first(self):
        self.stop_animation()
        self.canvas.reset()
        self.update_status_from_current_state()
        self.update_buttons_state()

    def go_to_last(self):
        self.stop_animation()
        self.canvas.last_state()
        self.update_status_from_current_state()
        self.update_buttons_state()

    def update_buttons_state(self):
        at_start = self.canvas.current_state_index == 0
        at_end = self.canvas.current_state_index == len(self.canvas.states) - 1

        self.first_btn.setEnabled(not at_start)
        self.prev_btn.setEnabled(not at_start)
        self.next_btn.setEnabled(not at_end)
        self.last_btn.setEnabled(not at_end)
        self.play_btn.setEnabled(not at_end)

    def update_status_from_current_state(self):
        if not self.canvas.states:
            return

        idx = self.canvas.current_state_index
        state = self.canvas.states[idx]

        # Get highlighted indices
        highlighted = state[1]

        # Create status message
        status = f"Step {idx}/{len(self.canvas.states) - 1}\n"
        status += f"Algorithm: {self.algo_combo.currentText()}\n"
        status += f"Comparisons: {state[4]}\n"
        status += f"Swaps: {state[5]}\n\n"

        if len(highlighted) == 2:
            status += f"Comparing/Swapping elements at indices {highlighted[0]} and {highlighted[1]}\n"
            status += f"Values: {state[0][highlighted[0]]} and {state[0][highlighted[1]]}"
        elif len(highlighted) == 1:
            status += f"Examining element at index {highlighted[0]}\n"
            status += f"Value: {state[0][highlighted[0]]}"

        # Add explanation based on current step and algorithm
        if self.current_algorithm and idx > 0:
            prev_state = self.canvas.states[idx - 1][0]
            curr_state = state[0]

            if prev_state != curr_state:
                # Find what changed
                changes = []
                for i in range(len(prev_state)):
                    if i < len(curr_state) and prev_state[i] != curr_state[i]:
                        changes.append(i)

                if changes and len(changes) == 2:
                    status += f"\n\nSwapped elements at indices {changes[0]} and {changes[1]}"
                    status += f"\nValues: {curr_state[changes[0]]} and {curr_state[changes[1]]}"

        self.status_text.setText(status)

    def update_status(self, message):
        current_text = self.status_text.toPlainText()
        self.status_text.setText(f"{message}\n\n{current_text}")

    def start_sorting(self):
        self.stop_animation()

        # Get selected algorithm
        algo_name = self.algo_combo.currentText()

        # Reset the states
        self.canvas.states = [(self.canvas.array.copy(), [], [], [], 0, 0)]
        self.canvas.current_state_index = 0
        self.canvas.comparison_count = 0
        self.canvas.swap_count = 0

        # Get sorting order
        ascending = self.order_asc.isChecked()

        # Run the selected algorithm
        if algo_name == "Bubble Sort":
            self.bubble_sort(ascending)
        elif algo_name == "Selection Sort":
            self.selection_sort(ascending)
        elif algo_name == "Insertion Sort":
            self.insertion_sort(ascending)
        elif algo_name == "Quick Sort":
            self.quick_sort_driver(ascending)
        elif algo_name == "Merge Sort":
            self.merge_sort_driver(ascending)

        self.current_algorithm = algo_name
        self.canvas.plot_state()
        self.update_status(f"Started {algo_name} algorithm")
        self.update_buttons_state()

    def bubble_sort(self, ascending=True):
        arr = self.canvas.array.copy()
        n = len(arr)

        # Track sorted indices (everything after n-i-1 is sorted)
        sorted_indices = []

        for i in range(n):
            swapped = False

            for j in range(0, n - i - 1):
                # Add state before comparison
                self.canvas.add_state(arr, [j, j + 1], sorted_indices)
                self.canvas.comparison_count += 1

                # Compare and swap if needed
                comparison = arr[j] > arr[j + 1] if ascending else arr[j] < arr[j + 1]
                if comparison:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    self.canvas.swap_count += 1

                    # Add state after swap
                    self.canvas.add_state(arr, [j, j + 1], sorted_indices)

            # Mark index n-i-1 as sorted
            sorted_indices.append(n - i - 1)

            # Add state showing the sorted index
            self.canvas.add_state(arr, [], sorted_indices)

            # If no swapping occurred, array is sorted
            if not swapped:
                break

        # Mark all elements as sorted in the final state
        self.canvas.add_state(arr, [], list(range(n)))

    def selection_sort(self, ascending=True):
        arr = self.canvas.array.copy()
        n = len(arr)

        # Track sorted indices
        sorted_indices = []

        for i in range(n):
            # Find the minimum/maximum element in remaining unsorted array
            opt_idx = i

            for j in range(i + 1, n):
                # Add state before comparison
                self.canvas.add_state(arr, [opt_idx, j], sorted_indices)
                self.canvas.comparison_count += 1

                # Compare elements
                comparison = arr[j] < arr[opt_idx] if ascending else arr[j] > arr[opt_idx]
                if comparison:
                    opt_idx = j

                    # Add state showing new min/max
                    self.canvas.add_state(arr, [opt_idx, j], sorted_indices)

            # Swap the found minimum/maximum element with the first element
            if opt_idx != i:
                arr[i], arr[opt_idx] = arr[opt_idx], arr[i]
                self.canvas.swap_count += 1

                # Add state after swap
                self.canvas.add_state(arr, [i, opt_idx], sorted_indices)

            # Mark index i as sorted
            sorted_indices.append(i)

            # Add state showing the sorted index
            self.canvas.add_state(arr, [], sorted_indices)

    def insertion_sort(self, ascending=True):
        arr = self.canvas.array.copy()
        n = len(arr)

        # Track sorted indices (indices before i are sorted)
        sorted_indices = [0]  # The first element is already sorted
        self.canvas.add_state(arr, [], sorted_indices)

        for i in range(1, n):
            key = arr[i]
            j = i - 1

            # Highlight the current element to be inserted
            self.canvas.add_state(arr, [i], sorted_indices)

            # Compare and shift elements until the correct position is found
            while j >= 0:
                self.canvas.comparison_count += 1

                # Highlight the comparison
                self.canvas.add_state(arr, [i, j], sorted_indices)

                comparison = arr[j] > key if ascending else arr[j] < key
                if not comparison:
                    break

                # Shift element
                arr[j + 1] = arr[j]
                self.canvas.swap_count += 1

                # Highlight the shift
                self.canvas.add_state(arr, [j + 1, j], sorted_indices)

                j -= 1

            # Place the key in its correct position
            arr[j + 1] = key

            # Update sorted indices
            sorted_indices = list(range(i + 1))

            # Add state showing the insertion
            self.canvas.add_state(arr, [j + 1], sorted_indices)

    def quick_sort_driver(self, ascending=True):
        arr = self.canvas.array.copy()
        self.quick_sort(arr, 0, len(arr) - 1, ascending)

        # Final state with all elements sorted
        self.canvas.add_state(arr, [], list(range(len(arr))))

    def quick_sort(self, arr, low, high, ascending=True):
        if low < high:
            # Find pivot index
            pi = self.partition(arr, low, high, ascending)

            # Sort elements before and after partition
            self.quick_sort(arr, low, pi - 1, ascending)
            self.quick_sort(arr, pi + 1, high, ascending)

    def partition(self, arr, low, high, ascending=True):
        pivot = arr[high]
        sorted_indices = []

        # Mark pivot
        self.canvas.add_state(arr, [high], sorted_indices, [high])

        i = low - 1

        for j in range(low, high):
            # Highlight current element being compared with pivot
            self.canvas.add_state(arr, [j, high], sorted_indices, [high])
            self.canvas.comparison_count += 1

            # Compare with pivot
            comparison = arr[j] <= pivot if ascending else arr[j] >= pivot
            if comparison:
                i += 1
                # Swap elements
                arr[i], arr[j] = arr[j], arr[i]
                self.canvas.swap_count += 1

                # Show the swap
                self.canvas.add_state(arr, [i, j], sorted_indices, [high])

        # Swap pivot to its final position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.canvas.swap_count += 1

        # Show the pivot swap
        self.canvas.add_state(arr, [i + 1, high], sorted_indices, [i + 1])

        # Mark the pivot as sorted
        sorted_indices.append(i + 1)
        self.canvas.add_state(arr, [], sorted_indices)

        return i + 1

    def merge_sort_driver(self, ascending=True):
        arr = self.canvas.array.copy()
        temp_arr = arr.copy()
        self.merge_sort(arr, temp_arr, 0, len(arr) - 1, ascending)

        # Final state with all elements sorted
        self.canvas.add_state(arr, [], list(range(len(arr))))

    def merge_sort(self, arr, temp_arr, left, right, ascending=True):
        if left < right:
            # Find middle point
            mid = (left + right) // 2

            # Highlight the current segment
            segment_indices = list(range(left, right + 1))
            self.canvas.add_state(arr, segment_indices, [])

            # Sort first and second halves
            self.merge_sort(arr, temp_arr, left, mid, ascending)
            self.merge_sort(arr, temp_arr, mid + 1, right, ascending)

            # Merge the sorted halves
            self.merge(arr, temp_arr, left, mid, right, ascending)

    def merge(self, arr, temp_arr, left, mid, right, ascending=True):
        # Highlight the segments being merged
        self.canvas.add_state(arr, list(range(left, right + 1)), [])

        # Copy data to temp arrays
        for i in range(left, right + 1):
            temp_arr[i] = arr[i]

        i = left  # Initial index of first subarray
        j = mid + 1  # Initial index of second subarray
        k = left  # Initial index of merged subarray

        while i <= mid and j <= right:
            # Highlight the elements being compared
            self.canvas.add_state(arr, [i, j], [])
            self.canvas.comparison_count += 1

            # Compare elements from both subarrays
            comparison = temp_arr[i] <= temp_arr[j] if ascending else temp_arr[i] >= temp_arr[j]
            if comparison:
                arr[k] = temp_arr[i]
                i += 1
            else:
                arr[k] = temp_arr[j]
                j += 1

            # Highlight the placement
            self.canvas.add_state(arr, [k], [])
            self.canvas.swap_count += 1
            k += 1

        # Copy the remaining elements
        while i <= mid:
            arr[k] = temp_arr[i]

            # Highlight the placement
            self.canvas.add_state(arr, [k, i], [])
            self.canvas.swap_count += 1

            i += 1
            k += 1

        while j <= right:
            arr[k] = temp_arr[j]

            # Highlight the placement
            self.canvas.add_state(arr, [k, j], [])
            self.canvas.swap_count += 1

            j += 1
            k += 1

        # Show the sorted segment
        sorted_segment = list(range(left, right + 1))
        self.canvas.add_state(arr, [], sorted_segment)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look across platforms
    main_window = SortingVisualizer()
    main_window.show()
    sys.exit(app.exec_())