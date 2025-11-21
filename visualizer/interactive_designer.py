"""
interactive cross section designer - drag boxes around and snap them together
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import TextBox, Button, RadioButtons
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cross_section_geometry.designs import design0, get_geometry_at_x
from src.analysis.failure_loads import calculate_failure_loads
from src.analysis.fos import find_FOS
from src.materials.material_properties import get_matboard_properties, get_glue_properties
from src.core.BME_SFE import SFEvals, BMEvals
from src.core.stress_envelope import get_section_properties, get_stress_envelope, get_max_glue_stress, get_web_compression_stress
from src.core.stresses import tau_cent
from src.core.buckling_analysis import get_buckling_capacities, get_flange_overhang_widths, get_stacked_thickness_vertical, get_stacked_thickness_horizontal
from src.core.geometric_properties import glue_width


class InteractiveDesigner:
    def __init__(self, geometry):
        self.geometry = geometry
        self.fig = plt.figure(figsize=(18, 10))  # wider for 3 columns
        self.ax = self.fig.add_axes([0.03, 0.15, 0.38, 0.8])  # main plot area - narrower
        self.rectangles = []  # list of (rect patch, plate dict, index)
        self.selected = None
        self.selected_plate = None
        self.dragging = False
        self.drag_offset = None
        self.snap_threshold = 2.0  # mm - how close to snap

        # glue joint dragging
        self.dragging_glue = False
        self.selected_glue_index = None

        # editor panel widgets
        self.editor_widgets = {}

        # envelope cache for BME/SFE - key is (loadcase, mass)
        self.envelope_cache = {}
        self.current_loadcase = 2
        self.current_mass = 1000

        # metrics panel text annotations
        self.metrics_text = None

        # glue joint visuals
        self.glue_lines = []  # list of Line2D objects

        self.setup_plot()
        self.setup_editor_panel()
        self.setup_metrics_panel()
        self.draw_all_plates()
        self.draw_glue_joints()
        self.connect_events()

    def setup_plot(self):
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Width (mm)', fontsize=12)
        self.ax.set_ylabel('Height (mm)', fontsize=12)
        self.ax.set_title('Interactive Designer - Drag plates, N=new plate, D=delete, G=add glue joint',
                         fontsize=11, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(-20, 120)
        self.ax.set_ylim(-20, 120)

    def setup_editor_panel(self):
        """create editor panel in middle column"""
        # title
        title_ax = self.fig.add_axes([0.44, 0.90, 0.18, 0.04])
        title_ax.text(0.5, 0.5, 'EDITOR', ha='center', va='center', fontsize=12, fontweight='bold')
        title_ax.axis('off')

        # width input
        width_ax = self.fig.add_axes([0.44, 0.80, 0.18, 0.05])
        self.editor_widgets['width'] = TextBox(width_ax, 'Width (b):', initial='')

        # height input
        height_ax = self.fig.add_axes([0.44, 0.70, 0.18, 0.05])
        self.editor_widgets['height'] = TextBox(height_ax, 'Height (h):', initial='')

        # plate type radio buttons
        type_ax = self.fig.add_axes([0.44, 0.48, 0.18, 0.18])
        self.editor_widgets['type'] = RadioButtons(type_ax, ['top_flange', 'web', 'bottom_flange'])

        # apply button
        apply_ax = self.fig.add_axes([0.44, 0.38, 0.08, 0.05])
        self.editor_widgets['apply'] = Button(apply_ax, 'Apply')
        self.editor_widgets['apply'].on_clicked(self.apply_edit)

        # delete button
        delete_ax = self.fig.add_axes([0.54, 0.38, 0.08, 0.05])
        self.editor_widgets['delete'] = Button(delete_ax, 'Delete')
        self.editor_widgets['delete'].on_clicked(self.delete_selected)

        # new plate button
        new_ax = self.fig.add_axes([0.44, 0.30, 0.18, 0.05])
        self.editor_widgets['new'] = Button(new_ax, 'New Plate')
        self.editor_widgets['new'].on_clicked(self.create_new_plate)

        # analyze button
        analyze_ax = self.fig.add_axes([0.44, 0.22, 0.18, 0.05])
        self.editor_widgets['analyze'] = Button(analyze_ax, 'Analyze (A)')
        self.editor_widgets['analyze'].on_clicked(self.run_analysis)

        # add glue joint button
        glue_ax = self.fig.add_axes([0.44, 0.16, 0.18, 0.04])
        self.editor_widgets['add_glue'] = Button(glue_ax, 'Add Glue Joint (G)')
        self.editor_widgets['add_glue'].on_clicked(self.add_glue_joint)

        # diaphragm spacing input
        spacing_ax = self.fig.add_axes([0.44, 0.09, 0.18, 0.05])
        initial_spacing = str(self.geometry.get('diaphragm_spacing', 150))
        self.editor_widgets['diaphragm_spacing'] = TextBox(spacing_ax, 'Spacing (a):', initial=initial_spacing)
        self.editor_widgets['diaphragm_spacing'].on_submit(self.update_diaphragm_spacing)

        # info text
        info_ax = self.fig.add_axes([0.44, 0.06, 0.18, 0.06])
        info_ax.text(0, 1, 'No plate selected', fontsize=9, va='top', wrap=True)
        info_ax.axis('off')
        self.editor_widgets['info_ax'] = info_ax

    def setup_metrics_panel(self):
        """create metrics panel on the right side"""
        # create axis for metrics display
        metrics_ax = self.fig.add_axes([0.64, 0.05, 0.34, 0.90])
        metrics_ax.axis('off')
        self.editor_widgets['metrics_ax'] = metrics_ax

        # initial placeholder text
        self.metrics_text = metrics_ax.text(
            0.05, 0.95,
            'No analysis yet\nMove or edit plates, then release\nto see live metrics',
            fontsize=9,
            va='top',
            family='monospace'
        )

    def draw_all_plates(self):
        # clear existing rectangles
        for rect, _, _ in self.rectangles:
            rect.remove()
        self.rectangles = []

        for i, plate in enumerate(self.geometry['plates']):
            self.add_plate_visual(plate, i)

    def draw_glue_joints(self):
        """draw red dashed lines for glue joints"""
        # clear existing glue lines
        for line in self.glue_lines:
            line.remove()
        self.glue_lines = []

        # get x range for lines
        x_min, x_max = self.ax.get_xlim()

        # draw each glue joint
        glue_joints = self.geometry.get('glue_joints', [])
        for y in glue_joints:
            line = self.ax.plot([x_min, x_max], [y, y], 'r--', linewidth=2, alpha=0.6, picker=5)[0]
            self.glue_lines.append(line)

        self.fig.canvas.draw()

    def add_plate_visual(self, plate, index):
        b = plate['b']
        h = plate['h']
        x_center = plate['x']
        y_center = plate['y']
        plate_type = plate['plate_type']

        x_corner = x_center - b / 2
        y_corner = y_center - h / 2

        # color based on plate type
        if plate_type == 'top_flange':
            color = 'steelblue'
        elif plate_type == 'web':
            color = 'darkgreen'
        elif plate_type == 'bottom_flange':
            color = 'coral'
        else:
            color = 'gray'

        rect = patches.Rectangle(
            (x_corner, y_corner), b, h,
            linewidth=2,
            edgecolor='black',
            facecolor=color,
            alpha=0.7,
            picker=True
        )
        self.ax.add_patch(rect)
        self.rectangles.append((rect, plate, index))

    def connect_events(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        # left click = select and prepare to drag
        if event.button == 1:
            clicked_something = False

            # check if clicked on a glue joint line
            for i, line in enumerate(self.glue_lines):
                if line.contains(event)[0]:
                    clicked_something = True
                    # start dragging this glue joint
                    self.dragging_glue = True
                    self.selected_glue_index = i
                    print(f"[glue] selected glue joint {i} for dragging")
                    return

            for rect, plate, index in self.rectangles:
                if rect.contains(event)[0]:
                    clicked_something = True
                    # select this plate and prepare for dragging
                    self.select_plate(rect, plate, index)
                    self.dragging = True
                    self.drag_offset = (event.xdata - plate['x'], event.ydata - plate['y'])
                    return

            # clicked empty space - deselect
            if not clicked_something:
                self.deselect_plate()

    def on_motion(self, event):
        if event.inaxes != self.ax:
            return

        # dragging glue joint
        if self.dragging_glue:
            glue_joints = self.geometry.get('glue_joints', [])
            if self.selected_glue_index < len(glue_joints):
                # update glue joint y position
                glue_joints[self.selected_glue_index] = event.ydata
                # redraw glue lines
                self.draw_glue_joints()
            return

        # dragging plate
        if self.dragging:
            rect, plate, _ = self.selected

            # update position
            new_x = event.xdata - self.drag_offset[0]
            new_y = event.ydata - self.drag_offset[1]

            plate['x'] = new_x
            plate['y'] = new_y

            # update rectangle
            x_corner = new_x - plate['b'] / 2
            y_corner = new_y - plate['h'] / 2
            rect.set_xy((x_corner, y_corner))

            self.fig.canvas.draw()

    def on_release(self, event):
        # releasing glue joint drag
        if self.dragging_glue:
            print(f"[release] glue joint released")
            glue_joints = self.geometry.get('glue_joints', [])
            if self.selected_glue_index < len(glue_joints):
                # snap to nearest plate edge
                y_current = glue_joints[self.selected_glue_index]
                plate_edges = []
                for plate in self.geometry['plates']:
                    top_edge = plate['y'] + plate['h'] / 2
                    bottom_edge = plate['y'] - plate['h'] / 2
                    plate_edges.append(top_edge)
                    plate_edges.append(bottom_edge)

                if plate_edges:
                    closest_edge = min(plate_edges, key=lambda edge: abs(edge - y_current))
                    if abs(closest_edge - y_current) < 2.0:  # snap within 2mm
                        glue_joints[self.selected_glue_index] = closest_edge
                        print(f"[glue] snapped to plate edge at y={closest_edge:.2f}")

                self.draw_glue_joints()
                self.update_metrics_panel()

            self.dragging_glue = False
            self.selected_glue_index = None
            return

        # releasing plate drag
        if not self.dragging:
            return

        print(f"[release] mouse released, plate moved")
        rect, plate, _ = self.selected

        # snap to nearest edges
        self.snap_to_edges(plate)

        # update rectangle after snapping
        x_corner = plate['x'] - plate['b'] / 2
        y_corner = plate['y'] - plate['h'] / 2
        rect.set_xy((x_corner, y_corner))

        self.dragging = False
        self.drag_offset = None
        self.fig.canvas.draw()

        # update metrics after plate movement
        self.update_metrics_panel()

    def on_key_press(self, event):
        """handle keyboard shortcuts"""
        if event.key in ['d', 'delete']:
            # check if hovering over glue joint
            if event.inaxes == self.ax and event.xdata and event.ydata:
                glue_joints = self.geometry.get('glue_joints', [])
                for i, y in enumerate(glue_joints):
                    if abs(event.ydata - y) < 2.0:  # within 2mm of glue joint
                        del glue_joints[i]
                        print(f"[glue] deleted glue joint at y={y:.2f}")
                        self.draw_glue_joints()
                        self.update_metrics_panel()
                        return
            # otherwise delete selected plate
            if self.selected_plate is not None:
                self.delete_selected(None)
        elif event.key == 'n':
            self.create_new_plate(None)
        elif event.key == 'a':
            self.run_analysis(None)
        elif event.key == 'g':
            self.add_glue_joint(None)

    def select_plate(self, rect, plate, index):
        """select a plate and update editor panel"""
        # unhighlight previous selection
        if self.selected is not None:
            prev_rect, _, _ = self.selected
            prev_rect.set_linewidth(2)
            prev_rect.set_edgecolor('black')

        # highlight new selection
        self.selected = (rect, plate, index)
        self.selected_plate = plate
        rect.set_linewidth(3)
        rect.set_edgecolor('red')

        # update editor panel
        self.editor_widgets['width'].set_val(str(plate['b']))
        self.editor_widgets['height'].set_val(str(plate['h']))
        self.editor_widgets['type'].set_active(['top_flange', 'web', 'bottom_flange'].index(plate['plate_type']))

        # update info
        self.update_info_text(f"Selected plate at ({plate['x']:.1f}, {plate['y']:.1f})")

        self.fig.canvas.draw()

    def deselect_plate(self):
        """deselect current plate"""
        if self.selected is not None:
            rect, _, _ = self.selected
            rect.set_linewidth(2)
            rect.set_edgecolor('black')

        self.selected = None
        self.selected_plate = None

        # clear editor fields
        self.editor_widgets['width'].set_val('')
        self.editor_widgets['height'].set_val('')

        self.update_info_text('No plate selected')
        self.fig.canvas.draw()

    def update_info_text(self, text):
        """update the info text in editor panel"""
        info_ax = self.editor_widgets['info_ax']
        info_ax.clear()
        info_ax.text(0, 1, text, fontsize=10, va='top', wrap=True)
        info_ax.axis('off')

    def update_diaphragm_spacing(self, text):
        """update diaphragm spacing value"""
        try:
            new_spacing = float(text)
            self.geometry['diaphragm_spacing'] = new_spacing
        except ValueError:
            pass

    def open_editor(self):
        """focus on editor panel (values already updated on selection)"""
        pass

    def apply_edit(self, event):
        """apply changes from editor panel"""
        if self.selected_plate is None:
            return

        try:
            plate = self.selected_plate

            # get values from textbox widgets
            new_width = self.editor_widgets['width'].text_disp.get_text()
            new_height = self.editor_widgets['height'].text_disp.get_text()

            plate['b'] = float(new_width)
            plate['h'] = float(new_height)

            # get selected radio button
            new_type = self.editor_widgets['type'].value_selected
            print(f"[edit] changing plate type to: {new_type}")
            plate['plate_type'] = new_type

            self.draw_all_plates()
            # reselect the same plate after redraw
            for rect, p, idx in self.rectangles:
                if p is plate:
                    self.select_plate(rect, p, idx)
                    break

            # update metrics after edit
            self.update_metrics_panel()
        except (ValueError, AttributeError) as e:
            print(f"[edit] error applying edit: {e}")
            import traceback
            traceback.print_exc()

    def delete_selected(self, event):
        """delete the selected plate"""
        if self.selected_plate is None:
            return

        _, _, index = self.selected
        self.geometry['plates'] = [p for i, p in enumerate(self.geometry['plates']) if i != index]
        self.selected = None
        self.selected_plate = None
        self.draw_all_plates()
        self.update_info_text('No plate selected')
        self.fig.canvas.draw()

        # update metrics after deletion
        self.update_metrics_panel()

    def create_new_plate(self, event):
        """create a new plate at center of view"""
        new_plate = {
            'b': 100.0,
            'h': 1.27,
            'x': 50.0,  # center of typical view
            'y': 50.0,
            'plate_type': 'top_flange'
        }
        self.geometry['plates'].append(new_plate)
        self.draw_all_plates()
        # auto-select the new plate
        for rect, p, idx in self.rectangles:
            if p is new_plate:
                self.select_plate(rect, p, idx)
                break

        # update metrics after creating new plate
        self.update_metrics_panel()

    def add_glue_joint(self, event):
        """add a glue joint at center of view, snapped to plate boundaries"""
        print(f"[glue] adding new glue joint...")

        # start at center of view
        y_target = 50.0

        # find all plate edges (where glue could go)
        plate_edges = []
        for plate in self.geometry['plates']:
            top_edge = plate['y'] + plate['h'] / 2
            bottom_edge = plate['y'] - plate['h'] / 2
            plate_edges.append(top_edge)
            plate_edges.append(bottom_edge)

        # snap to nearest plate edge
        if plate_edges:
            closest_edge = min(plate_edges, key=lambda edge: abs(edge - y_target))
            snap_threshold = 5.0  # snap within 5mm
            if abs(closest_edge - y_target) < snap_threshold:
                y_target = closest_edge
                print(f"[glue] snapped to plate edge at y={y_target:.2f}")
            else:
                print(f"[glue] no nearby edge, using y={y_target:.2f}")

        # check if glue joint already exists at this y
        glue_joints = self.geometry.get('glue_joints', [])
        for existing_y in glue_joints:
            if abs(existing_y - y_target) < 0.1:  # within 0.1mm
                print(f"[glue] glue joint already exists at y={y_target:.2f}")
                return

        # add the glue joint
        if 'glue_joints' not in self.geometry:
            self.geometry['glue_joints'] = []
        self.geometry['glue_joints'].append(y_target)
        print(f"[glue] added glue joint at y={y_target:.2f}")

        # redraw glue joints
        self.draw_glue_joints()

        # update metrics
        self.update_metrics_panel()

    def snap_to_edges(self, plate):
        """snap plate edges to nearby plate edges and to zero line"""
        # get edges of current plate
        left = plate['x'] - plate['b'] / 2
        right = plate['x'] + plate['b'] / 2
        top = plate['y'] + plate['h'] / 2
        bottom = plate['y'] - plate['h'] / 2

        best_snap_x = None
        best_snap_y = None
        best_dist_x = self.snap_threshold
        best_dist_y = self.snap_threshold

        # snap to zero line for y
        if abs(bottom) < self.snap_threshold:
            candidate_y = plate['h'] / 2  # move so bottom edge is at y=0
            if not self.would_overlap(plate, candidate_y, plate['x']):
                best_snap_y = candidate_y
                best_dist_y = 0
        if abs(top) < self.snap_threshold:
            candidate_y = -plate['h'] / 2  # move so top edge is at y=0
            if not self.would_overlap(plate, candidate_y, plate['x']):
                best_snap_y = candidate_y
                best_dist_y = 0

        # snap to zero line for x
        if abs(left) < self.snap_threshold:
            candidate_x = plate['b'] / 2  # move so left edge is at x=0
            if not self.would_overlap(plate, plate['y'], candidate_x):
                best_snap_x = candidate_x
                best_dist_x = 0
        if abs(right) < self.snap_threshold:
            candidate_x = -plate['b'] / 2  # move so right edge is at x=0
            if not self.would_overlap(plate, plate['y'], candidate_x):
                best_snap_x = candidate_x
                best_dist_x = 0

        # check against all other plates
        for _, other_plate, _ in self.rectangles:
            if other_plate is plate:
                continue

            other_left = other_plate['x'] - other_plate['b'] / 2
            other_right = other_plate['x'] + other_plate['b'] / 2
            other_top = other_plate['y'] + other_plate['h'] / 2
            other_bottom = other_plate['y'] - other_plate['h'] / 2

            # check all edge combinations for x
            x_snaps = [
                (left, other_left, 0),  # left to left
                (left, other_right, 0),  # left to right
                (right, other_left, 0),  # right to left
                (right, other_right, 0),  # right to right
            ]

            for edge, other_edge, _ in x_snaps:
                dist = abs(edge - other_edge)
                if dist < best_dist_x:
                    offset = other_edge - edge
                    candidate_x = plate['x'] + offset
                    if not self.would_overlap(plate, plate['y'], candidate_x):
                        best_dist_x = dist
                        best_snap_x = candidate_x

            # check all edge combinations for y
            y_snaps = [
                (top, other_top, 0),  # top to top
                (top, other_bottom, 0),  # top to bottom
                (bottom, other_top, 0),  # bottom to top
                (bottom, other_bottom, 0),  # bottom to bottom
            ]

            for edge, other_edge, _ in y_snaps:
                dist = abs(edge - other_edge)
                if dist < best_dist_y:
                    offset = other_edge - edge
                    candidate_y = plate['y'] + offset
                    if not self.would_overlap(plate, candidate_y, plate['x']):
                        best_dist_y = dist
                        best_snap_y = candidate_y

        # apply snaps
        if best_snap_x is not None:
            plate['x'] = best_snap_x
        if best_snap_y is not None:
            plate['y'] = best_snap_y

    def get_cached_envelopes(self, loadcase, mass):
        """get or calculate cached BME/SFE"""
        cache_key = (loadcase, mass)
        if cache_key not in self.envelope_cache:
            print(f"[cache] calculating envelopes for loadcase={loadcase}, mass={mass}...")
            # calculate and cache the envelopes
            sfe_min, sfe_max = SFEvals(loadcase, mass)
            bme_min, bme_max = BMEvals(loadcase, mass)
            self.envelope_cache[cache_key] = {
                'sfe_min': sfe_min,
                'sfe_max': sfe_max,
                'bme_min': bme_min,
                'bme_max': bme_max
            }
            print(f"[cache] envelopes cached")
        else:
            print(f"[cache] using cached envelopes for loadcase={loadcase}, mass={mass}")
        return self.envelope_cache[cache_key]

    def calculate_live_metrics(self):
        """
        calculate all metrics for live display
        returns dict with section props, stresses, buckling details, FOS, etc
        """
        print(f"[metrics] starting calculation...")
        # material props
        matboard = get_matboard_properties()
        glue = get_glue_properties()
        material_props = {**matboard, **glue}

        # get cached envelopes
        envelopes = self.get_cached_envelopes(self.current_loadcase, self.current_mass)
        sfe_min = envelopes['sfe_min']
        sfe_max = envelopes['sfe_max']
        bme_min = envelopes['bme_min']
        bme_max = envelopes['bme_max']

        # find critical location by sweeping all 10,000 points
        bridge_length = 1250
        num_points = 10000
        x_vals = [i * bridge_length / (num_points - 1) for i in range(num_points)]

        min_fos_overall = float('inf')
        critical_x = 0
        critical_metrics = None

        for i, x in enumerate(x_vals):
            # get geometry at x
            plates, glue_joints = get_geometry_at_x(self.geometry, x)
            if not plates:
                continue

            # section properties
            props = get_section_properties(plates, glue_joints)

            # envelope values at this point
            V_env = max(abs(sfe_min[i]), abs(sfe_max[i]))
            M_max = bme_max[i]
            M_min = bme_min[i]

            # stresses
            stresses = get_stress_envelope(M_max, M_min, props['y_top'], props['y_bot'], props['I'])
            tau_c = tau_cent(V_env, props['Q_cent'], props['I'], props['b_cent'])
            tau_glue_max = get_max_glue_stress(plates, glue_joints, V_env, props['I'])

            # buckling
            E = material_props['E']
            nu = material_props['nu']
            diaphragm_spacing = self.geometry.get('diaphragm_spacing')
            buckling = get_buckling_capacities(plates, E, nu, props['ybar'], diaphragm_spacing=diaphragm_spacing)

            # web compression stress for case 3
            sigma_web = get_web_compression_stress(buckling['web_plates'], M_max, M_min, props['ybar'], props['I']) if buckling['web_plates'] else 0

            # calculate FOS values
            def calc_fos(applied, capacity):
                if abs(applied) < 1e-10:
                    return float('inf')
                return capacity / abs(applied)

            fos_tens = calc_fos(stresses['tension_max'], material_props['sigma_tens'])
            fos_comp = calc_fos(stresses['compression_max'], material_props['sigma_comp'])
            fos_shear = calc_fos(tau_c, material_props['tau_max'])
            fos_glue = calc_fos(tau_glue_max, material_props['tau_glue_max'])
            fos_buck1 = calc_fos(stresses['top_compression'], buckling['top_flange_inside'])
            fos_buck2 = calc_fos(stresses['top_compression'], buckling['top_flange_overhang'])
            fos_buck3 = calc_fos(sigma_web, buckling['web']) if buckling['web_plates'] else float('inf')
            fos_buckV = calc_fos(tau_c, buckling['shear'])

            # find overall min
            all_fos = [fos_tens, fos_comp, fos_shear, fos_glue, fos_buck1, fos_buck2, fos_buck3, fos_buckV]
            local_min_fos = min(all_fos)

            if local_min_fos < min_fos_overall:
                min_fos_overall = local_min_fos
                critical_x = x

                # get detailed info for critical location
                web_plates = [p for p in plates if p.get('plate_type') == 'web']
                top_plates = [p for p in plates if p.get('plate_type') == 'top_flange']

                # calculate area
                total_area = sum(p['b'] * p['h'] for p in plates)

                # calculate max glue width
                max_glue_width = 0
                if glue_joints:
                    for glue_y in glue_joints:
                        gw = glue_width(plates, glue_y)
                        max_glue_width = max(max_glue_width, gw)

                # buckling dimensions
                if top_plates:
                    overhang_info = get_flange_overhang_widths(top_plates, web_plates)
                    t_top = get_stacked_thickness_vertical(top_plates)
                    b_case1 = overhang_info['inside_width']
                    b_case2 = overhang_info['max_overhang']
                else:
                    t_top = 0
                    b_case1 = 0
                    b_case2 = 0

                if web_plates:
                    web_top = max(p['y'] + p['h']/2 for p in web_plates)
                    b_case3 = web_top - props['ybar']  # compression zone height
                    t_web = get_stacked_thickness_horizontal(web_plates)
                    h_web = max(p['h'] for p in web_plates)
                    a_spacing = diaphragm_spacing if diaphragm_spacing else 0
                else:
                    b_case3 = 0
                    t_web = 0
                    h_web = 0
                    a_spacing = 0

                # failure mode
                fos_dict = {
                    'Tension': fos_tens,
                    'Compression': fos_comp,
                    'Shear': fos_shear,
                    'Glue': fos_glue,
                    'Buck case 1': fos_buck1,
                    'Buck case 2': fos_buck2,
                    'Buck case 3': fos_buck3,
                    'Shear buck': fos_buckV
                }
                failure_mode = min(fos_dict, key=fos_dict.get)

                critical_metrics = {
                    # section properties
                    'ybar': props['ybar'],
                    'I': props['I'],
                    'area': total_area,
                    'y_top': props['y_top'],
                    'y_bot': props['y_bot'],

                    # applied stresses
                    'tension_stress': stresses['tension_max'],
                    'compression_stress': stresses['compression_max'],
                    'top_compression_stress': stresses['top_compression'],
                    'shear_stress': tau_c,
                    'glue_stress': tau_glue_max,
                    'web_compression_stress': sigma_web,

                    # buckling case 1
                    'buck1_t': t_top,
                    'buck1_b': b_case1,
                    'buck1_capacity': buckling['top_flange_inside'],
                    'fos_buck1': fos_buck1,

                    # buckling case 2
                    'buck2_t': t_top,
                    'buck2_b': b_case2,
                    'buck2_capacity': buckling['top_flange_overhang'],
                    'fos_buck2': fos_buck2,

                    # buckling case 3
                    'buck3_t': t_web,
                    'buck3_b': b_case3,
                    'buck3_capacity': buckling['web'],
                    'fos_buck3': fos_buck3,

                    # shear buckling
                    'buckV_h': h_web,
                    'buckV_t': t_web,
                    'buckV_a': a_spacing,
                    'buckV_capacity': buckling['shear'],
                    'fos_buckV': fos_buckV,

                    # glue
                    'glue_width': max_glue_width,
                    'fos_glue': fos_glue,

                    # other FOS
                    'fos_tens': fos_tens,
                    'fos_comp': fos_comp,
                    'fos_shear': fos_shear,

                    # overall
                    'min_fos': min_fos_overall,
                    'failure_mode': failure_mode,
                    'max_load': min_fos_overall * self.current_mass,
                    'critical_x': critical_x
                }

        print(f"[metrics] done - min FOS: {min_fos_overall:.2f} at x={critical_x:.1f}mm")
        return critical_metrics if critical_metrics else {}

    def update_metrics_panel(self):
        """update the metrics display with current geometry"""
        print(f"[update] updating metrics panel...")
        try:
            metrics = self.calculate_live_metrics()

            if not metrics:
                text = 'No plates in geometry'
                print(f"[update] no metrics to display")
            else:
                print(f"[update] formatting metrics display...")
                # format the metrics display
                lines = []
                lines.append('SECTION PROPERTIES')
                lines.append(f'  ybar:      {metrics["ybar"]:.2f} mm')
                lines.append(f'  I:         {metrics["I"]:.1f} mm^4')
                lines.append(f'  area:      {metrics["area"]:.2f} mm^2')
                lines.append(f'  y_top:     {metrics["y_top"]:.2f} mm')
                lines.append(f'  y_bot:     {metrics["y_bot"]:.2f} mm')
                lines.append('')

                lines.append('APPLIED STRESSES (at critical x)')
                lines.append(f'  tension:    {metrics["tension_stress"]:.2f} MPa')
                lines.append(f'  comp:       {metrics["compression_stress"]:.2f} MPa')
                lines.append(f'  top comp:   {metrics["top_compression_stress"]:.2f} MPa')
                lines.append(f'  shear:      {metrics["shear_stress"]:.3f} MPa')
                lines.append(f'  glue:       {metrics["glue_stress"]:.3f} MPa')
                lines.append(f'  web comp:   {metrics["web_compression_stress"]:.2f} MPa')
                lines.append('')

                lines.append('BUCKLING CASE 1 (top flange inside)')
                lines.append(f'  t:          {metrics["buck1_t"]:.2f} mm')
                lines.append(f'  b:          {metrics["buck1_b"]:.2f} mm')
                cap1 = metrics["buck1_capacity"]
                lines.append(f'  capacity:   {cap1:.1f} MPa' if cap1 != float('inf') else '  capacity:   inf MPa')
                fos1 = metrics["fos_buck1"]
                lines.append(f'  FOS:        {fos1:.2f}' if fos1 != float('inf') else '  FOS:        inf')
                lines.append('')

                lines.append('BUCKLING CASE 2 (top flange overhang)')
                lines.append(f'  t:          {metrics["buck2_t"]:.2f} mm')
                lines.append(f'  b:          {metrics["buck2_b"]:.2f} mm')
                cap2 = metrics["buck2_capacity"]
                lines.append(f'  capacity:   {cap2:.1f} MPa' if cap2 != float('inf') else '  capacity:   inf MPa')
                fos2 = metrics["fos_buck2"]
                lines.append(f'  FOS:        {fos2:.2f}' if fos2 != float('inf') else '  FOS:        inf')
                lines.append('')

                lines.append('BUCKLING CASE 3 (web)')
                lines.append(f'  t:          {metrics["buck3_t"]:.2f} mm')
                lines.append(f'  b:          {metrics["buck3_b"]:.2f} mm')
                cap3 = metrics["buck3_capacity"]
                lines.append(f'  capacity:   {cap3:.1f} MPa' if cap3 != float('inf') else '  capacity:   inf MPa')
                fos3 = metrics["fos_buck3"]
                lines.append(f'  FOS:        {fos3:.2f}' if fos3 != float('inf') else '  FOS:        inf')
                lines.append('')

                lines.append('SHEAR BUCKLING')
                lines.append(f'  h:          {metrics["buckV_h"]:.2f} mm')
                lines.append(f'  t:          {metrics["buckV_t"]:.2f} mm')
                lines.append(f'  a:          {metrics["buckV_a"]:.2f} mm')
                capV = metrics["buckV_capacity"]
                lines.append(f'  capacity:   {capV:.3f} MPa' if capV != float('inf') else '  capacity:   inf MPa')
                fosV = metrics["fos_buckV"]
                lines.append(f'  FOS:        {fosV:.2f}' if fosV != float('inf') else '  FOS:        inf')
                lines.append('')

                lines.append('GLUE SHEAR')
                lines.append(f'  glue width: {metrics["glue_width"]:.2f} mm')
                lines.append(f'  FOS:        {metrics["fos_glue"]:.2f}')
                lines.append('')

                lines.append('SUMMARY')
                lines.append(f'  min FOS:    {metrics["min_fos"]:.2f}')
                lines.append(f'  failure:    {metrics["failure_mode"]}')
                lines.append(f'  max load:   {metrics["max_load"]:.1f} N')
                lines.append(f'  at x:       {metrics["critical_x"]:.1f} mm')

                text = '\n'.join(lines)

            # update text
            self.metrics_text.set_text(text)
            print(f"[update] metrics text updated, redrawing canvas...")
            self.fig.canvas.draw()
            print(f"[update] done")

        except Exception as e:
            print(f"[update] ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.metrics_text.set_text(f'Error calculating metrics:\n{str(e)}')
            self.fig.canvas.draw()

    def run_analysis(self, event):
        """run structural analysis on current cross section"""
        print("\n" + "="*50)
        print("STRUCTURAL ANALYSIS")
        print("="*50)

        # setup material properties
        matboard = get_matboard_properties()
        glue = get_glue_properties()
        material_props = {**matboard, **glue}

        # run analysis for loadcase 2, 1000N train
        loadcase = 2
        mass = 1000  # N

        try:
            results = calculate_failure_loads(self.geometry, loadcase, mass, material_props)

            print(f"\nCross section analysis (loadcase {loadcase}, train mass {mass}N)")
            print(f"Diaphragm spacing: {self.geometry.get('diaphragm_spacing', 150)} mm")
            print(f"Number of plates: {len(self.geometry['plates'])}")
            print()

            # find minimum FOS for each failure mode
            min_fos_tens = min(results['fos_tens'])
            min_fos_comp = min(results['fos_comp'])
            min_fos_shear = min(results['fos_shear'])
            min_fos_glue = min(results['fos_glue'])
            min_fos_buck1 = min(results['fos_buck1'])
            min_fos_buck2 = min(results['fos_buck2'])
            min_fos_buck3 = min(results['fos_buck3'])
            min_fos_buckV = min(results['fos_buckV'])
            fos_euler = results['fos_euler']

            print("Factor of Safety (FOS) for each failure mode:")
            print(f"  Tension (matboard):                {min_fos_tens:.2f}")
            print(f"  Compression (matboard):            {min_fos_comp:.2f}")
            print(f"  Shear (matboard):                  {min_fos_shear:.2f}")
            print(f"  Glue shear:                        {min_fos_glue:.2f}")
            print(f"  Buckling (top flange):             {min_fos_buck1:.2f}")
            print(f"  Buckling (top flange overhang):    {min_fos_buck2:.2f}")
            print(f"  Buckling (web):                    {min_fos_buck3:.2f}")
            print(f"  Buckling (shear):                  {min_fos_buckV:.2f}")
            print(f"  Euler buckling (global):           {fos_euler:.2f}")
            print()

            # determine limiting failure mode
            all_fos = {
                'Tension': min_fos_tens,
                'Compression': min_fos_comp,
                'Shear': min_fos_shear,
                'Glue shear': min_fos_glue,
                'Buckling (top flange)': min_fos_buck1,
                'Buckling (top flange overhang)': min_fos_buck2,
                'Buckling (web)': min_fos_buck3,
                'Buckling (shear)': min_fos_buckV,
                'Euler buckling': fos_euler
            }
            limiting_mode = min(all_fos, key=all_fos.get)

            print(f"Overall minimum FOS:          {results['overall_min_fos']:.2f}")
            print(f"Limiting failure mode:        {limiting_mode}")
            print(f"Maximum load capacity:        {results['failure_load']:.1f} N")
            print("="*50 + "\n")

        except Exception as e:
            print(f"Analysis failed: {e}")
            print("="*50 + "\n")

    def would_overlap(self, plate, new_y, new_x):
        """check if plate at new position would overlap with any other plate"""
        new_left = new_x - plate['b'] / 2
        new_right = new_x + plate['b'] / 2
        new_top = new_y + plate['h'] / 2
        new_bottom = new_y - plate['h'] / 2

        for _, other_plate, _ in self.rectangles:
            if other_plate is plate:
                continue

            other_left = other_plate['x'] - other_plate['b'] / 2
            other_right = other_plate['x'] + other_plate['b'] / 2
            other_top = other_plate['y'] + other_plate['h'] / 2
            other_bottom = other_plate['y'] - other_plate['h'] / 2

            # check if rectangles overlap (not just touching)
            # touching edges (distance = 0) is allowed, overlapping (distance < 0) is not
            x_overlap = (new_left < other_right - 0.01) and (new_right > other_left + 0.01)
            y_overlap = (new_bottom < other_top - 0.01) and (new_top > other_bottom + 0.01)

            if x_overlap and y_overlap:
                return True

        return False

    def print_geometry(self):
        """print current geometry as python code"""
        print("\n" + "="*60)
        print("current geometry:")
        print("="*60)
        print("plates = [")
        for plate in self.geometry['plates']:
            print(f"    {{'b': {plate['b']}, 'h': {plate['h']}, " +
                  f"'x': {plate['x']:.3f}, 'y': {plate['y']:.3f}, " +
                  f"'plate_type': '{plate['plate_type']}'}},")
        print("]")
        print()
        glue_joints = self.geometry.get('glue_joints', [])
        print(f"glue_joints = {[round(y, 2) for y in glue_joints]}")
        print()
        print(f"diaphragm_spacing = {self.geometry.get('diaphragm_spacing', 150)}")
        print()

    def show(self):
        plt.show()
        # print geometry when window closes
        self.print_geometry()


if __name__ == "__main__":
    import sys

    print("starting interactive designer...")
    print("controls:")
    print("  - click+drag plate: move plate")
    print("  - click+drag glue line: move glue joint")
    print("  - N: create new plate")
    print("  - G: add glue joint (snaps to plate edges)")
    print("  - D or Delete: delete selected plate or glue joint (hover over it)")
    print("  - A: run structural analysis")
    print("  - click empty space: deselect")
    print()

    # get design from command line argument or default to design0
    if len(sys.argv) > 1:
        design_name = sys.argv[1]
        try:
            from src.cross_section_geometry.designs import __dict__ as designs_dict
            if design_name in designs_dict and callable(designs_dict[design_name]):
                geometry = designs_dict[design_name]()
                print(f"loaded design: {design_name}")
            else:
                print(f"design '{design_name}' not found, using design0")
                geometry = design0()
        except Exception as e:
            print(f"error loading design '{design_name}': {e}")
            print("using design0")
            geometry = design0()
    else:
        print("no design specified, using design0")
        print("usage: python interactive_designer.py [design_name]")
        geometry = design0()

    print(f"loaded {len(geometry['plates'])} plates")
    print(f"loaded {len(geometry.get('glue_joints', []))} glue joints")
    designer = InteractiveDesigner(geometry)
    designer.show()
