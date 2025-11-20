"""
draw cross sections! yay!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cross_section_geometry.designs import simple_square, design0


def draw_cross_section(geometry, title="Bridge Cross Section"):

    fig, ax = plt.subplots(figsize=(10, 8))

    for plate in geometry['plates']:
        b = plate['b']  
        h = plate['h'] 
        x_center = plate['x']
        y_center = plate['y']
        plate_type = plate['plate_type']

        x_corner = x_center - b / 2
        y_corner = y_center - h / 2

        # color based on plate type!
        if plate_type == 'top_flange':
            color = 'steelblue'
            label = 'Top Flange'
        elif plate_type == 'web':
            color = 'darkgreen'
            label = 'Web'
        elif plate_type == 'bottom_flange':
            color = 'coral'
            label = 'Bottom Flange'

        rect = patches.Rectangle(
            (x_corner, y_corner), b, h,
            linewidth=1.5,
            edgecolor='black',
            facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)

    # glue joints = dashed red lines
    if 'glue_joints' in geometry:
        for y_glue in geometry['glue_joints']:
            all_x = [plate['x'] for plate in geometry['plates']]
            all_b = [plate['b'] for plate in geometry['plates']]
            x_min = min([x - b/2 for x, b in zip(all_x, all_b)])
            x_max = max([x + b/2 for x, b in zip(all_x, all_b)])

            ax.plot([x_min, x_max], [y_glue, y_glue],
                   'r--', linewidth=2, label='Glue Joint')

    ax.set_aspect('equal')
    ax.set_xlabel('Width (mm)', fontsize=12)
    ax.set_ylabel('Height (mm)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    geometry = design0()
    draw_cross_section(geometry, title="Design 0")
