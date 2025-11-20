"""
analyze bridge cross-section designs
"""

from src.materials.material_properties import get_matboard_properties, get_glue_properties
from src.analysis.failure_loads import calculate_failure_loads, find_critical_location
from src.visualization.make_plots import plot_sfe_bme, plot_fos_along_bridge, plot_failure_loads
import os

def analyze_design(geometry, loadcase, mass, output_dir=None):
    """
    run the full analysis on a bridge design

    Input =
        geometry: bridge geometry dict
        loadcase: 1, 2, or 3
        mass: train mass (N)
        output_dir: where to save plots (optional)

    Output =
        failure_load, overall_min_fos, all FOS arrays
    """

    print(f"\nloadcase {loadcase}, mass {mass}N")

    # get material properties
    matboard = get_matboard_properties()
    glue = get_glue_properties()
    material_props = {**matboard, **glue}

    # calculate failure loads
    failure_results = calculate_failure_loads(geometry, loadcase, mass, material_props)

    # find critical location
    critical = find_critical_location(failure_results)

    # print summary
    idx = critical['index']
    print(f"\nmin FOS: {failure_results['overall_min_fos']} at x={failure_results['x'][idx]}mm")
    print(f"failure load: {failure_results['failure_load']}N")
    print(f"tension: {failure_results['fos_tens'][idx]}, compression: {failure_results['fos_comp'][idx]}")
    print(f"shear: {failure_results['fos_shear'][idx]}, glue: {failure_results['fos_glue'][idx]}")
    print(f"buckling: {failure_results['fos_buck1'][idx]}, {failure_results['fos_buck2'][idx]}, {failure_results['fos_buck3'][idx]}, shear buck: {failure_results['fos_buckV'][idx]}")

    # generate plots if output directory specified
    if output_dir:
        print(f"\ngenerating plots in {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        plot_sfe_bme(loadcase, mass, save_path=os.path.join(output_dir, 'sfe_bme.png'))
        plot_fos_along_bridge(failure_results, save_path=os.path.join(output_dir, 'fos_along_bridge.png'))
        plot_failure_loads(failure_results, save_path=os.path.join(output_dir, 'failure_loads.png'))

    return failure_results
