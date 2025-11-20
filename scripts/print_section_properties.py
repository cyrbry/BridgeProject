"""
calculate and print section properties for a design
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.geometric_properties import y_bar, I, Q
from src.cross_section_geometry.designs import design0, simple_square

def print_section_properties(geometry, design_name="design"):
    """
    calculate and print I, ybar, and Q for a cross section

    Input =
        geometry: dict from design function with 'plates' and 'glue_joints'
        design_name: name for display
    """
    plates = geometry['plates']

    # calculate geometric properties
    ybar = y_bar(plates)
    I_val = I(plates)
    Q_cent = Q(plates, ybar)

    print(f"{design_name} section properties:")
    print(f"ybar: {ybar} mm")
    print(f"I: {I_val} mm^4")
    print(f"Q (at centroid): {Q_cent} mm^3")


if __name__ == "__main__":
    geometry = design0()
    print_section_properties(geometry, design_name="design0")
