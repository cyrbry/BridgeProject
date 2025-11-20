"""
calculate and plot BMD and SFD for a specific train position and load case
"""

import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.reactions_BMD_SFD import SFDvals, BMDvals
from src.cross_section_geometry.designs import design0, simple_square

def plot_bmd_sfd(x, loadcase, mass, design_name="design"):
    """
    calculate and plot BMD and SFD for a given train position

    Input =
        x: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train (N)
        design_name: name for the plot title
    """
    # calculate SFD and BMD
    sfd = SFDvals(x, loadcase, mass)
    bmd = BMDvals(x, loadcase, mass)

    # create position array (10,000 points from 0 to 1250)
    num_points = 10000
    bridge_length = 1250
    positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]

    # create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # plot SFD
    ax1.plot(positions, sfd, 'b-', linewidth=1.5)
    ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax1.axvline(x=25, color='r', linestyle='--', linewidth=1, label='Support A')
    ax1.axvline(x=1225, color='r', linestyle='--', linewidth=1, label='Support B')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Position along bridge (mm)')
    ax1.set_ylabel('Shear Force (N)')
    ax1.set_title(f'Shear Force Diagram - {design_name} (x={x}mm, loadcase={loadcase}, mass={mass}N)')
    ax1.legend()

    # plot BMD
    ax2.plot(positions, bmd, 'g-', linewidth=1.5)
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax2.axvline(x=25, color='r', linestyle='--', linewidth=1, label='Support A')
    ax2.axvline(x=1225, color='r', linestyle='--', linewidth=1, label='Support B')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Position along bridge (mm)')
    ax2.set_ylabel('Bending Moment (N·mm)')
    ax2.set_title(f'Bending Moment Diagram - {design_name}')
    ax2.legend()

    plt.tight_layout()
    plt.show()

    # print some stats
    max_shear = max(max(sfd), abs(min(sfd)))
    max_moment = max(bmd)
    min_moment = min(bmd)

    print(f"max shear: {max_shear} N")
    print(f"max moment: {max_moment} N·mm")
    print(f"min moment: {min_moment} N·mm")


if __name__ == "__main__":
    # loadcase 2: locomotive (182N) + 2 regular cars (135N each)
    x = 197
    loadcase = 2
    mass = 452

    plot_bmd_sfd(x, loadcase, mass, design_name="design0")
