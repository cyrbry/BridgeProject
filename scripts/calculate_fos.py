"""
calculate and display FOS for a design at a specific train position
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cross_section_geometry.designs import design0, simple_square
from src.core.reactions_BMD_SFD import SFDvals, BMDvals
from src.materials.material_properties import get_matboard_properties, get_glue_properties
from src.analysis.fos import find_FOS

def calculate_and_print_fos(x_train, loadcase, mass, geometry, design_name="design"):
    """
    calculate FOS for all failure modes at midspan

    Input =
        x_train: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train (N)
        geometry: dict from design function
        design_name: name for display
    """
    # calculate SFD and BMD at the train position
    sfd = SFDvals(x_train, loadcase, mass)
    bmd = BMDvals(x_train, loadcase, mass)

    # find midspan (halfway between supports at 25mm and 1225mm)
    midspan_index = int((625 / 1250) * 10000)  # 625mm is midspan

    V_midspan = sfd[midspan_index]
    M_midspan = bmd[midspan_index]

    # get material properties
    matboard = get_matboard_properties()
    glue = get_glue_properties()
    material_props = {**matboard, **glue}

    # calculate FOS at midspan
    fos_results = find_FOS(625, geometry, V_midspan, M_midspan, M_midspan, material_props)

    print(f"{design_name} FOS at midspan:")
    print(f"  train position x={x_train}mm, loadcase={loadcase}, mass={mass}N")
    print(f"  V at midspan: {V_midspan} N")
    print(f"  M at midspan: {M_midspan} N·mm")
    print()
    print(f"  FOS tension: {fos_results['fos_tens']}")
    print(f"  FOS compression: {fos_results['fos_comp']}")
    print(f"  FOS shear: {fos_results['fos_shear']}")
    print(f"  FOS glue: {fos_results['fos_glue']}")
    print(f"  FOS buckling case 1 (top flange): {fos_results['fos_buck1']}")
    print(f"  FOS buckling case 2 (web): {fos_results['fos_buck2']}")
    print(f"  FOS buckling case 3 (bottom flange): {fos_results['fos_buck3']}")
    print(f"  FOS shear buckling: {fos_results['fos_buckV']}")
    print()
    print(f"  min FOS: {fos_results['min_fos']}")
    print(f"  failure mode: {fos_results['failure_mode']}")


if __name__ == "__main__":
    # loadcase 2: locomotive (182N) + 2 regular cars (135N each)
    x = 197
    loadcase = 2
    mass = 452

    geometry = design0()
    calculate_and_print_fos(x, loadcase, mass, geometry, design_name="design0")
