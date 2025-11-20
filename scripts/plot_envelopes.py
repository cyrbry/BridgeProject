"""
calculate and plot shear force and bending moment envelopes
"""

import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.BME_SFE import SFEvals, BMEvals

def plot_envelopes(loadcase, mass, design_name="design"):
    """
    calculate and plot SFE and BME for a given load case

    Input =
        loadcase: 1, 2, or 3
        mass: total mass of train (N)
        design_name: name for the plot title
    """
    print(f"Calculating envelopes for loadcase {loadcase}, mass {mass}N...")

    # calculate envelopes
    sfe_min, sfe_max = SFEvals(loadcase, mass)
    bme_min, bme_max = BMEvals(loadcase, mass)

    # create position array (10,000 points from 0 to 1250)
    num_points = 10000
    bridge_length = 1250
    positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]

    # create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # plot SFE
    ax1.plot(positions, sfe_max, 'b-', linewidth=1.5, label='Max Shear')
    ax1.plot(positions, sfe_min, 'r-', linewidth=1.5, label='Min Shear')
    ax1.fill_between(positions, sfe_min, sfe_max, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax1.axvline(x=25, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Support A')
    ax1.axvline(x=1225, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Support B')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Position along bridge (mm)')
    ax1.set_ylabel('Shear Force (N)')
    ax1.set_title(f'Shear Force Envelope - {design_name} (loadcase={loadcase}, mass={mass}N)')
    ax1.legend()

    # plot BME
    ax2.plot(positions, bme_max, 'b-', linewidth=1.5, label='Max Moment')
    ax2.plot(positions, bme_min, 'r-', linewidth=1.5, label='Min Moment')
    ax2.fill_between(positions, bme_min, bme_max, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax2.axvline(x=25, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Support A')
    ax2.axvline(x=1225, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Support B')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Position along bridge (mm)')
    ax2.set_ylabel('Bending Moment (N·mm)')
    ax2.set_title(f'Bending Moment Envelope - {design_name}')
    ax2.legend()

    plt.tight_layout()
    plt.show()

    # print some stats
    max_shear_pos = max(sfe_max)
    max_shear_neg = abs(min(sfe_min))
    max_shear = max(max_shear_pos, max_shear_neg)
    max_moment = max(bme_max)
    min_moment = min(bme_min)

    print(f"\nmax shear (positive): {max_shear_pos} N")
    print(f"max shear (negative): {max_shear_neg} N")
    print(f"max absolute shear: {max_shear} N")
    print(f"max moment: {max_moment} N·mm")
    print(f"min moment: {min_moment} N·mm")


if __name__ == "__main__":
    # TA values
    loadcase = 2
    mass = 452

    plot_envelopes(loadcase, mass, design_name="design0")
