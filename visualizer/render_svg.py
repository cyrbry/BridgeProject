import matplotlib.pyplot as plt
import matplotlib.patches as patches

rects = [
    {'x': 0, 'y': 393, 'width': 1016, 'height': 420},
    {'x': 0.0, 'y': 40.553759952774726, 'width': 420, 'height': 250},
    {'x': 0.23577, 'y': 292.32427, 'width': 1016, 'height': 100},
    {'x': 420.0, 'y': 41.66772678866607, 'width': 100, 'height': 250},
    {'x': 520.0, 'y': 177.6544785242031, 'width': 72.5, 'height': 115},
    {'x': 592.5, 'y': 177.6544785242031, 'width': 72.5, 'height': 115},
    {'x': 665.0, 'y': 178.46948841794574, 'width': 72.5, 'height': 115},
    {'x': 737.5, 'y': 178.79969694214878, 'width': 72.5, 'height': 115},
    {'x': 810.0, 'y': 177.8433805312868, 'width': 72.5, 'height': 115},
    {'x': 882.5, 'y': 177.6544785242031, 'width': 72.5, 'height': 115},
    {'x': 520.0, 'y': 61.6458496812279, 'width': 72.5, 'height': 115},
    {'x': 592.5, 'y': 61.908838099173636, 'width': 72.5, 'height': 115},
    {'x': 665.0, 'y': 62.13536799291637, 'width': 72.5, 'height': 115},
    {'x': 737.5, 'y': 63.28058641086204, 'width': 72.5, 'height': 115},
    {'x': 810.0, 'y': 63.28058641086204, 'width': 72.5, 'height': 115},
    {'x': 882.5, 'y': 63.61079493506509, 'width': 72.5, 'height': 115},
]

SVG_HEIGHT = 813


class EditableSVGViewer:
    def __init__(self, rects_list):
        self.rects = [dict(r) for r in rects_list]
        self.snap_threshold = 5.0

        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 11))
        self.rectangles = []
        self.selected = None
        self.selected_rect = None
        self.dragging = False
        self.drag_offset = None

        self.setup_plot()
        self.draw_all_rects()
        self.connect_events()

    def setup_plot(self):
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X (mm)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y (mm)', fontsize=12, fontweight='bold')
        self.ax.set_title('Cut Out Plan',
                          fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.15, linestyle='--')
        self.ax.set_xlim(-200, 1200)
        self.ax.set_ylim(-120, 850)

    def draw_all_rects(self):
        for patch, _, _ in self.rectangles:
            patch.remove()
        self.rectangles = []

        for i, rect in enumerate(self.rects):
            self.add_rect_visual(rect, i)

        self.draw_dimension_labels()
        self.fig.canvas.draw()

    def add_rect_visual(self, rect, index):
        x = rect['x']
        y = SVG_HEIGHT - rect['y'] - rect['height']
        w = rect['width']
        h = rect['height']

        patch = patches.Rectangle((x, y), w, h,
                                   linewidth=2, edgecolor='black',
                                   facecolor='lightblue', alpha=0.5,
                                   picker=True)
        self.ax.add_patch(patch)
        self.rectangles.append((patch, rect, index))

    def draw_dimension_labels(self):
        """draw length labels on edges that are external"""
        # find all edges
        edges = {}  # key: (orientation, position), value: list of (start, end)

        for rect in self.rects:
            x = rect['x']
            y = SVG_HEIGHT - rect['y'] - rect['height']
            w = rect['width']
            h = rect['height']

            # horizontal edges (top and bottom)
            top_key = ('h', y)
            if top_key not in edges:
                edges[top_key] = []
            edges[top_key].append((x, x + w))

            bottom_key = ('h', y + h)
            if bottom_key not in edges:
                edges[bottom_key] = []
            edges[bottom_key].append((x, x + w))

            # vertical edges (left and right)
            left_key = ('v', x)
            if left_key not in edges:
                edges[left_key] = []
            edges[left_key].append((y, y + h))

            right_key = ('v', x + w)
            if right_key not in edges:
                edges[right_key] = []
            edges[right_key].append((y, y + h))

        # find external segments and label them
        for (orient, pos), segments in edges.items():
            # sort segments
            segments.sort()

            # identify continuous external segments
            for start, end in segments:
                # check if this segment is truly external (not covered by others)
                covered = False
                for other_start, other_end in segments:
                    if other_start <= start < other_end or other_start < end <= other_end:
                        if (other_start, other_end) != (start, end):
                            covered = True
                            break

                if not covered:
                    length = end - start
                    mid = (start + end) / 2

                    if orient == 'h':
                        # horizontal edge - label above/below
                        self.ax.text(mid, pos - 15, f'{length:.1f}', ha='center', va='top',
                                    fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
                    else:
                        # vertical edge - label left/right
                        self.ax.text(pos - 15, mid, f'{length:.1f}', ha='right', va='center',
                                    fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    def connect_events(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        if event.button == 1:
            clicked = False

            for patch, rect, index in self.rectangles:
                if patch.contains(event)[0]:
                    clicked = True
                    self.select_rect(patch, rect, index)
                    self.dragging = True
                    self.drag_offset = (event.xdata - rect['x'], event.ydata - (SVG_HEIGHT - rect['y'] - rect['height'] + rect['height']/2))
                    return

            if not clicked:
                self.deselect_rect()

    def on_motion(self, event):
        if event.inaxes != self.ax or not self.dragging:
            return

        patch, rect, _ = self.selected

        new_x = event.xdata - self.drag_offset[0]
        rect['x'] = new_x

        screen_y = event.ydata
        svg_y = SVG_HEIGHT - (screen_y + rect['height']/2)
        rect['y'] = svg_y

        screen_y_corner = SVG_HEIGHT - rect['y'] - rect['height']
        patch.set_xy((new_x, screen_y_corner))

        self.fig.canvas.draw()

    def on_release(self, _):
        if not self.dragging:
            return

        self.dragging = False
        self.drag_offset = None

        patch, rect, _ = self.selected
        self.snap_to_edges(rect)

        screen_y_corner = SVG_HEIGHT - rect['y'] - rect['height']
        patch.set_xy((rect['x'], screen_y_corner))

        self.draw_all_rects()

    def snap_to_edges(self, rect):
        """snap rect edges to nearby rect edges"""
        left = rect['x']
        right = rect['x'] + rect['width']
        top_screen = SVG_HEIGHT - rect['y']
        bottom_screen = SVG_HEIGHT - rect['y'] - rect['height']

        best_snap_x = None
        best_snap_y = None
        best_dist_x = self.snap_threshold
        best_dist_y = self.snap_threshold

        for other_rect in self.rects:
            if other_rect is rect:
                continue

            other_left = other_rect['x']
            other_right = other_rect['x'] + other_rect['width']
            other_top_screen = SVG_HEIGHT - other_rect['y']
            other_bottom_screen = SVG_HEIGHT - other_rect['y'] - other_rect['height']

            x_pairs = [
                (left, other_left),
                (left, other_right),
                (right, other_left),
                (right, other_right),
            ]

            for edge, other_edge in x_pairs:
                dist = abs(edge - other_edge)
                if dist < best_dist_x:
                    offset = other_edge - edge
                    best_snap_x = rect['x'] + offset
                    best_dist_x = dist

            y_pairs = [
                (top_screen, other_top_screen),
                (top_screen, other_bottom_screen),
                (bottom_screen, other_top_screen),
                (bottom_screen, other_bottom_screen),
            ]

            for edge, other_edge in y_pairs:
                dist = abs(edge - other_edge)
                if dist < best_dist_y:
                    offset = other_edge - edge
                    best_snap_y = rect['y'] + offset
                    best_dist_y = dist

        if best_snap_x is not None:
            rect['x'] = best_snap_x
        if best_snap_y is not None:
            rect['y'] = best_snap_y

    def on_key_press(self, event):
        if event.key == 'd' or event.key == 'delete':
            if self.selected_rect is not None:
                _, _, index = self.selected
                self.rects = [r for i, r in enumerate(self.rects) if i != index]
                self.selected = None
                self.selected_rect = None
                self.draw_all_rects()

        elif event.key == 'n':
            new_rect = {'x': 500, 'y': 400, 'width': 100, 'height': 100}
            self.rects.append(new_rect)
            self.draw_all_rects()

    def select_rect(self, patch, rect, index):
        if self.selected is not None:
            prev_patch, _, _ = self.selected
            prev_patch.set_linewidth(2)
            prev_patch.set_edgecolor('black')

        self.selected = (patch, rect, index)
        self.selected_rect = rect
        patch.set_linewidth(3)
        patch.set_edgecolor('red')
        self.fig.canvas.draw()

    def deselect_rect(self):
        if self.selected is not None:
            patch, _, _ = self.selected
            patch.set_linewidth(2)
            patch.set_edgecolor('black')

        self.selected = None
        self.selected_rect = None
        self.fig.canvas.draw()

    def print_rects(self):
        print("\n" + "="*60)
        print("final rectangles:")
        print("="*60)
        print("rects = [")
        for rect in self.rects:
            print(f"    {{'x': {rect['x']}, 'y': {rect['y']}, 'width': {rect['width']}, 'height': {rect['height']}}},")
        print("]")
        print()

    def show(self):
        plt.show()
        self.print_rects()


if __name__ == "__main__":
    viewer = EditableSVGViewer(rects)
    viewer.show()
