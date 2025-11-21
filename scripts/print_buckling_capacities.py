"""
calculate and print buckling capacities for a design
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.buckling_analysis import get_buckling_capacities, get_unsupported_width, get_flange_overhang_widths, get_stacked_thickness_vertical
from src.core.geometric_properties import y_bar
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

    # calculate neutral axis
    neutral_axis_y = y_bar(plates)
    diaphragm_spacing = geometry.get('diaphragm_spacing')

    # get buckling capacities
    buckling = get_buckling_capacities(plates, material['E'], material['nu'], neutral_axis_y, diaphragm_spacing=diaphragm_spacing)

    # get plate groups for dimension info
    web_plates = [p for p in plates if p.get('plate_type') == 'web']
    top_plates = [p for p in plates if p.get('plate_type') == 'top_flange']
    bottom_plates = [p for p in plates if p.get('plate_type') == 'bottom_flange']

    print(f"{design_name} buckling capacities:")
    print(f"  E = {material['E']} MPa, nu = {material['nu']}")
    print()

    # top flange inside (case 1, k=4)
    if top_plates:
        overhang_info = get_flange_overhang_widths(top_plates, web_plates)
        t_top = get_stacked_thickness_vertical(top_plates)
        print(f"  top flange inside buckling (case 1, k=4):")
        print(f"    inside width b = {overhang_info['inside_width']:.2f} mm")
        print(f"    thickness t = {t_top:.2f} mm")
        print(f"    sigma_crit = {buckling['top_flange_inside']:.2f} MPa")
        print()
        print(f"  top flange overhang buckling (case 2, k=0.425):")
        print(f"    max overhang = {overhang_info['max_overhang']:.2f} mm")
        print(f"    thickness t = {t_top:.2f} mm")
        print(f"    sigma_crit = {buckling['top_flange_overhang']:.2f} MPa")
    else:
        print(f"  top flange: none")
    print()

    # web compression zone (case 3, k=6)
    if web_plates:
        web_top = max(p['y'] + p['h']/2 for p in web_plates)
        compression_zone_height = web_top - neutral_axis_y
        t_web = max(p['b'] for p in web_plates)
        print(f"  web buckling (case 3, k=6):")
        print(f"    compression zone height = {compression_zone_height:.2f} mm")
        print(f"    thickness t = {t_web:.2f} mm")
        print(f"    sigma_crit = {buckling['web']:.2f} MPa")
    else:
        print(f"  web: none")
    print()

    # shear buckling
    if web_plates:
        print(f"  shear buckling:")
        print(f"    tau_crit = {buckling['shear']:.2f} MPa")
        if diaphragm_spacing:
            print(f"    (with diaphragm spacing = {diaphragm_spacing} mm)")
    else:
        print(f"  shear buckling: no webs")


if __name__ == "__main__":
    geometry = design0()
    print_buckling_capacities(geometry, design_name="design0")
