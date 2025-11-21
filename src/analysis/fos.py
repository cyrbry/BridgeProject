"""
calculate factor of safety for all failure modes at a location along the bridge
"""

from src.core.stresses import tau_cent
from src.cross_section_geometry.designs import get_geometry_at_x
from src.core.stress_envelope import (
    get_section_properties,
    get_stress_envelope,
    get_max_glue_stress,
    get_web_compression_stress
)
from src.core.buckling_analysis import get_buckling_capacities

def calculate_fos(applied, capacity):
    """
    calculate factor of safety = capacity / applied

    stops division by zero ooh ahh fancy
    """
    if abs(applied) < (10 ** -10):
        return float('inf')
    return capacity / abs(applied)

def find_FOS(x_position, geometry, V_env, M_max, M_min, material_props):
    """
    calculate FOS for all failure modes at position x

    Input =
        x_position: position along bridge (mm)
        geometry: bridge geometry dict
        V_env: shear force envelope at x (N)
        M_max, M_min: max and min bending moments at x (N·mm)
        material_props: matboard and glue properties

    Outputs =
        dict with all the fos and the failure_mode
    """

    # get geometry at this x position
    plates, glue_joints = get_geometry_at_x(geometry, x_position)

    # calculate section properties
    props = get_section_properties(plates, glue_joints)

    # find stress envelope
    stresses = get_stress_envelope(M_max, M_min, props['y_top'], props['y_bot'], props['I'])

    # calculate applied stresses
    tau_c = tau_cent(V_env, props['Q_cent'], props['I'], props['b_cent'])
    tau_glue_max = get_max_glue_stress(plates, glue_joints, V_env, props['I'])

    # get buckling capacities
    E = material_props['E']
    nu = material_props['nu']
    diaphragm_spacing = geometry.get('diaphragm_spacing')
    buckling = get_buckling_capacities(plates, E, nu, props['ybar'], diaphragm_spacing=diaphragm_spacing)

    # calculate all FOS values
    fos_tens = calculate_fos(stresses['tension_max'], material_props['sigma_tens'])
    fos_comp = calculate_fos(stresses['compression_max'], material_props['sigma_comp'])
    fos_sh = calculate_fos(tau_c, material_props['tau_max'])
    fos_gl = calculate_fos(tau_glue_max, material_props['tau_glue_max'])

    # buckling FOS
    # case 1: top flange inside (k=4) vs top compression
    fos_b1 = calculate_fos(stresses['top_compression'], buckling['top_flange_inside'])

    # case 2: top flange overhang (k=0.425) vs top compression (same stress as case 1)
    fos_b2 = calculate_fos(stresses['top_compression'], buckling['top_flange_overhang'])

    # case 3: web (k=6) vs compression at top of web
    sigma_web = get_web_compression_stress(buckling['web_plates'], M_max, M_min, props['ybar'], props['I'])
    fos_b3 = calculate_fos(sigma_web, buckling['web']) if buckling['web_plates'] else float('inf')

    # shear buckling
    fos_bV = calculate_fos(tau_c, buckling['shear'])

    # find minimum FOS and failure mode
    fos_dict = {
        'tension': fos_tens,
        'compression': fos_comp,
        'shear': fos_sh,
        'glue': fos_gl,
        'flexural_buckling_case1': fos_b1,
        'flexural_buckling_case2': fos_b2,
        'flexural_buckling_case3': fos_b3,
        'shear_buckling': fos_bV
    }

    min_fos_value = min(fos_dict.values())
    failure_mode = min(fos_dict, key=fos_dict.get)

    return {
        'fos_tens': fos_tens,
        'fos_comp': fos_comp,
        'fos_shear': fos_sh,
        'fos_glue': fos_gl,
        'fos_buck1': fos_b1,
        'fos_buck2': fos_b2,
        'fos_buck3': fos_b3,
        'fos_buckV': fos_bV,
        'min_fos': min_fos_value,
        'failure_mode': failure_mode
    }
