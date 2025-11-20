"""
calculate failure loads and capacities along the bridge
"""

from src.core.BME_SFE import SFEvals, BMEvals
from src.analysis.fos import find_FOS

def calculate_failure_loads(geometry, loadcase, mass, material_props, num_points=10000):
    """
    calculate Vfail and Mfail along the bridge, plus FOS for each failure mode

    Input =
        geometry: bridge geometry dict
        loadcase: 1, 2, or 3
        mass: train mass (N)
        material_props: matboard and glue properties
        num_points: number of points along bridge (default 10000)

    Output = dict with x positions, envelopes, FOS arrays for each mode, failure capacities, overall_min_fos, failure_load
    """

    # calculate shear force and bending moment envelopes
    sfe_min, sfe_max = SFEvals(loadcase, mass)
    bme_min, bme_max = BMEvals(loadcase, mass)

    # take maximum absolute values for shear envelope
    V_env = [max(abs(sfe_min[i]), abs(sfe_max[i])) for i in range(num_points)]
    M_max = bme_max
    M_min = bme_min
    
    bridge_length = 1250  # mm
    x_positions = [i * bridge_length / (num_points - 1) for i in range(num_points)]
    
    fos_tens_array = []
    fos_comp_array = []
    fos_shear_array = []
    fos_glue_array = []
    fos_buck1_array = []
    fos_buck2_array = []
    fos_buck3_array = []
    fos_buckV_array = []
    min_fos_array = []

    # calculate FOS at each position
    for i, x in enumerate(x_positions):
        fos_results = find_FOS(x, geometry, V_env[i], M_max[i], M_min[i], material_props)

        fos_tens_array.append(fos_results['fos_tens'])
        fos_comp_array.append(fos_results['fos_comp'])
        fos_shear_array.append(fos_results['fos_shear'])
        fos_glue_array.append(fos_results['fos_glue'])
        fos_buck1_array.append(fos_results['fos_buck1'])
        fos_buck2_array.append(fos_results['fos_buck2'])
        fos_buck3_array.append(fos_results['fos_buck3'])
        fos_buckV_array.append(fos_results['fos_buckV'])
        min_fos_array.append(fos_results['min_fos'])
    
    # calculate Vfail and Mfail for each failure mode
    Vfail_shear = [fos_shear_array[i] * V_env[i] for i in range(num_points)]
    Vfail_glue = [fos_glue_array[i] * V_env[i] for i in range(num_points)]
    Vfail_buckV = [fos_buckV_array[i] * V_env[i] for i in range(num_points)]

    # for moment failures, use the envelope magnitude
    M_env_mag = [max(abs(M_max[i]), abs(M_min[i])) for i in range(num_points)]
    Mfail_tens = [fos_tens_array[i] * M_env_mag[i] for i in range(num_points)]
    Mfail_comp = [fos_comp_array[i] * M_env_mag[i] for i in range(num_points)]
    Mfail_buck1 = [fos_buck1_array[i] * M_env_mag[i] for i in range(num_points)]
    Mfail_buck2 = [fos_buck2_array[i] * M_env_mag[i] for i in range(num_points)]
    Mfail_buck3 = [fos_buck3_array[i] * M_env_mag[i] for i in range(num_points)]
    
    # find overall minimum FOS
    overall_min_fos = min(min_fos_array)
    failure_load = overall_min_fos * mass
    
    return {
        'x': x_positions,
        'V_env': V_env,
        'M_max': M_max,
        'M_min': M_min,
        'M_env': [max(abs(M_max[i]), abs(M_min[i])) for i in range(num_points)],  # for backward compatibility
        'fos_tens': fos_tens_array,
        'fos_comp': fos_comp_array,
        'fos_shear': fos_shear_array,
        'fos_glue': fos_glue_array,
        'fos_buck1': fos_buck1_array,
        'fos_buck2': fos_buck2_array,
        'fos_buck3': fos_buck3_array,
        'fos_buckV': fos_buckV_array,
        'min_fos': min_fos_array,
        'Vfail_shear': Vfail_shear,
        'Vfail_glue': Vfail_glue,
        'Vfail_buckV': Vfail_buckV,
        'Mfail_tens': Mfail_tens,
        'Mfail_comp': Mfail_comp,
        'Mfail_buck1': Mfail_buck1,
        'Mfail_buck2': Mfail_buck2,
        'Mfail_buck3': Mfail_buck3,
        'overall_min_fos': overall_min_fos,
        'failure_load': failure_load
    }

def find_critical_location(failure_results):
    """
    find the location with minimum FOS

    Input = failure_results dict from calculate_failure_loads()
    Output = dict with x position (mm), min_fos value, and array index
    """
    min_fos_array = failure_results['min_fos']
    min_fos_value = min(min_fos_array)
    min_index = min_fos_array.index(min_fos_value)
    x_critical = failure_results['x'][min_index]
    
    return {
        'x': x_critical,
        'min_fos': min_fos_value,
        'index': min_index
    }
