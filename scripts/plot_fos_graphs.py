"""
generate FOS along bridge plots for calc report
- Design 0, Load Case 1, 400N
- Cigar design, Load Case 2, 452N
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cross_section_geometry.designs import design0, cigar
from src.analysis.failure_loads import calculate_failure_loads
from src.materials.material_properties import get_matboard_properties, get_glue_properties
from src.visualization.make_plots import plot_fos_along_bridge

def generate_fos_plot(geometry, loadcase, mass, design_name, output_path):
    """
    calculate and save FOS along bridge plot

    Input =
        geometry: bridge geometry dict
        loadcase: 1, 2, or 3
        mass: train mass (N)
        design_name: name for the plot
        output_path: path to save the graph
    """
    print(f"Generating FOS plot for {design_name} (loadcase {loadcase}, mass {mass}N)...")

    # get material properties
    matboard = get_matboard_properties()
    glue = get_glue_properties()
    material_props = {**matboard, **glue}

    # calculate failure loads
    failure_results = calculate_failure_loads(geometry, loadcase, mass, material_props)

    # plot FOS with title
    title = f'FOS values along bridge for {design_name} under Load Case {loadcase} ({mass}N)'
    plot_fos_along_bridge(failure_results, save_path=output_path, title=title)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    base_path = os.path.join(os.path.dirname(__file__), '..', 'not_code', 'images_for_calc_report')

    # Design 0, Load Case 1, 400N
    generate_fos_plot(
        geometry=design0(),
        loadcase=1,
        mass=400,
        design_name="Design 0",
        output_path=os.path.join(base_path, "FOS_design0_loadcase1.png")
    )

    # Cigar design, Load Case 2, 452N
    generate_fos_plot(
        geometry=cigar(),
        loadcase=2,
        mass=452,
        design_name="Cigar (Final Design)",
        output_path=os.path.join(base_path, "FOS_cigar_loadcase2.png")
    )

    print("\nDone!")
