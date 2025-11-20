"""
calculate and print buckling capacities for a design
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.buckling_analysis import get_buckling_capacities, get_unsupported_width
from src.materials.material_properties import get_matboard_properties
from src.cross_section_geometry.designs import design0, simple_square

def print_buckling_capacities(geometry, design_name="design"):
    """
    calculate and print all buckling capacities for a cross section

    Input =
        geometry: dict from design function with 'plates' and 'glue_joints'
        design_name: name for display
    """
    plates = geometry['plates']
    material = get_matboard_properties()

    # get buckling capacities
    buckling = get_buckling_capacities(plates, material['E'], material['nu'])

    # get plate groups for dimension info
    web_plates = [p for p in plates if p.get('plate_type') == 'web']
    top_plates = [p for p in plates if p.get('plate_type') == 'top_flange']
    bottom_plates = [p for p in plates if p.get('plate_type') == 'bottom_flange']

    print(f"{design_name} buckling capacities:")
    print(f"  E = {material['E']} MPa, nu = {material['nu']}")
    print()

    # top flange
    if top_plates:
        b_top = get_unsupported_width(top_plates, web_plates)
        t_top = min(p['h'] for p in top_plates)
        print(f"  top flange buckling (case 1):")
        print(f"    unsupported width b = {b_top} mm")
        print(f"    thickness t = {t_top} mm")
        print(f"    sigma_crit = {buckling['top_flange']} MPa")
    else:
        print(f"  top flange: none")
    print()

    # web
    if web_plates:
        h_web = max(p['h'] for p in web_plates)
        t_web = max(p['b'] for p in web_plates)
        print(f"  web buckling (case 2):")
        print(f"    height h = {h_web} mm")
        print(f"    thickness t = {t_web} mm")
        print(f"    sigma_crit = {buckling['web']} MPa")
    else:
        print(f"  web: none")
    print()

    # bottom flange
    if bottom_plates:
        b_bottom = get_unsupported_width(bottom_plates, web_plates)
        t_bottom = min(p['h'] for p in bottom_plates)
        print(f"  bottom flange buckling (case 3):")
        print(f"    unsupported width b = {b_bottom} mm")
        print(f"    thickness t = {t_bottom} mm")
        print(f"    sigma_crit = {buckling['bottom_flange']} MPa")
    else:
        print(f"  bottom flange: none")
    print()

    # shear buckling
    if web_plates:
        print(f"  shear buckling:")
        print(f"    tau_crit = {buckling['shear']} MPa")
    else:
        print(f"  shear buckling: no webs")


if __name__ == "__main__":
    geometry = design0()
    print_buckling_capacities(geometry, design_name="design0")
