"""
calculate and print stresses for a design at a specific train position
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.reactions_BMD_SFD import SFDvals, BMDvals
from src.core.stress_envelope import get_section_properties
from src.core.stresses import sigma_top, sigma_bot, tau_cent, tau_glue
from src.core.geometric_properties import Q, glue_width
from src.cross_section_geometry.designs import design0

def print_stresses(geometry, x_train, loadcase, mass, design_name="design"):
    """
    calculate and print stresses for a train position using max M and V from that position's BMD/SFD

    Input =
        geometry: dict from design function with 'plates' and 'glue_joints'
        x_train: position of leftmost wheel (mm from left edge of bridge)
        loadcase: 1, 2, or 3
        mass: total mass of train
        design_name: name for display
    """
    plates = geometry['plates']
    glue_joints = geometry['glue_joints']

    # get section properties
    props = get_section_properties(plates, glue_joints)

    # get full BMD and SFD for this train position
    sfd = SFDvals(x_train, loadcase, mass)
    bmd = BMDvals(x_train, loadcase, mass)

    # find max values from the diagrams
    M_max = max(bmd)
    M_min = min(bmd)
    V_max = max(max(sfd), abs(min(sfd)))

    # use the larger magnitude moment for stress calc
    M = M_max if abs(M_max) > abs(M_min) else M_min

    # flexural stresses using max moment
    sigma_t = sigma_top(M, props['y_top'], props['I'])
    sigma_b = sigma_bot(M, props['y_bot'], props['I'])

    # shear stress at centroid using max shear
    tau = tau_cent(V_max, props['Q_cent'], props['I'], props['b_cent'])

    # glue shear stresses
    tau_glue_vals = []
    for glue_y in glue_joints:
        Q_glue = Q(plates, glue_y)
        b_glue = glue_width(plates, glue_y)
        if b_glue > 0:
            tau_g = tau_glue(V_max, Q_glue, props['I'], b_glue)
            tau_glue_vals.append((glue_y, tau_g))

    # web compression
    web_plates = [p for p in plates if p.get('plate_type') == 'web']
    if web_plates:
        web_top_y = max(p['y'] + p['h']/2 for p in web_plates)
        web_top_dist = web_top_y - props['ybar']
        sigma_web = -M * web_top_dist / props['I']
    else:
        sigma_web = 0

    print(f"{design_name} stresses (train at x = {x_train} mm):")
    print(f"  loadcase {loadcase}, mass {mass} g")
    print(f"  ybar = {props['ybar']} mm, I = {props['I']} mm^4")
    print()

    print(f"  M_max = {M_max} N·mm")
    print(f"  M_min = {M_min} N·mm")
    print(f"  V_max = {V_max} N")
    print(f"  using M = {M} N·mm for stress calc")
    print()

    print(f"  flexural stresses:")
    print(f"    sigma_top = {sigma_t} MPa")
    print(f"    sigma_bottom = {sigma_b} MPa")
    print()

    print(f"  shear stress at centroid:")
    print(f"    tau = {tau} MPa")
    print()

    if tau_glue_vals:
        print(f"  glue shear stresses:")
        for glue_y, tau_g in tau_glue_vals:
            print(f"    at y = {glue_y} mm: tau = {tau_g} MPa")
        print()

    print(f"  web compression at top: {sigma_web} MPa")


if __name__ == "__main__":
    # loadcase 2: locomotive (182N) + 2 regular cars (135N each)
    x = 197
    loadcase = 2
    mass = 452

    geometry = design0()
    print_stresses(geometry, x_train=x, loadcase=loadcase, mass=mass, design_name="design0")
