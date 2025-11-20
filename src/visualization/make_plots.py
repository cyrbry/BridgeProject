"""
generate plots for design calculations deliverable
"""

import matplotlib.pyplot as plt
from src.core.BME_SFE import SFEvals, BMEvals
from src.analysis.failure_loads import calculate_failure_loads
from src.materials.material_properties import get_matboard_properties, get_glue_properties
import os

def plot_sfe_bme(loadcase, mass, save_path=None):
    """
    plot shear force and bending moment envelopes
    
    Input = 
        loadcase: 1, 2, or 3
        mass: train mass (N)
        save_path: path to save figure (optional, if None will show instead)
    """
    # calculate envelopes
    sfe_min, sfe_max = SFEvals(loadcase, mass)
    bme_min, bme_max = BMEvals(loadcase, mass)
    
    # create x positions
    num_points = len(sfe_min)
    x = [i * 1250 / (num_points - 1) for i in range(num_points)]
    
    # create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # plot SFE
    ax1.plot(x, sfe_max, 'b-', linewidth=2, label='Max shear')
    ax1.plot(x, sfe_min, 'r-', linewidth=2, label='Min shear')
    ax1.fill_between(x, sfe_min, sfe_max, alpha=0.2)
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax1.axvline(x=25, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Supports')
    ax1.axvline(x=1225, color='g', linestyle='--', linewidth=1, alpha=0.5)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Position along bridge (mm)')
    ax1.set_ylabel('Shear Force (N)')
    ax1.set_title(f'Shear Force Envelope - Load Case {loadcase}, Mass={mass}N')
    ax1.legend()
    
    # plot BME
    ax2.plot(x, bme_max, 'b-', linewidth=2, label='Max moment')
    ax2.plot(x, bme_min, 'r-', linewidth=2, label='Min moment')
    ax2.fill_between(x, bme_min, bme_max, alpha=0.2)
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax2.axvline(x=25, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Supports')
    ax2.axvline(x=1225, color='g', linestyle='--', linewidth=1, alpha=0.5)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Position along bridge (mm)')
    ax2.set_ylabel('Bending Moment (N·mm)')
    ax2.set_title(f'Bending Moment Envelope - Load Case {loadcase}, Mass={mass}N')
    ax2.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_fos_along_bridge(failure_results, save_path=None):
    """
    plot all FOS values along bridge length
    
    Input = 
        failure_results: dict from calculate_failure_loads()
        save_path: path to save figure (optional)
    """
    x = failure_results['x']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # plot each FOS
    ax.plot(x, failure_results['fos_tens'], label='Tension', linewidth=2)
    ax.plot(x, failure_results['fos_comp'], label='Compression', linewidth=2)
    ax.plot(x, failure_results['fos_shear'], label='Shear', linewidth=2)
    ax.plot(x, failure_results['fos_glue'], label='Glue', linewidth=2)
    ax.plot(x, failure_results['fos_buck1'], label='Flexural Buckling Case 1', linewidth=1.5, linestyle='--')
    ax.plot(x, failure_results['fos_buck2'], label='Flexural Buckling Case 2', linewidth=1.5, linestyle='--')
    ax.plot(x, failure_results['fos_buck3'], label='Flexural Buckling Case 3', linewidth=1.5, linestyle='--')
    ax.plot(x, failure_results['fos_buckV'], label='Shear Buckling', linewidth=1.5, linestyle='--')
    ax.plot(x, failure_results['min_fos'], 'k-', label='Minimum FOS', linewidth=3)
    
    # add horizontal line at FOS = 1
    ax.axhline(y=1, color='r', linestyle=':', linewidth=2, label='FOS = 1 (failure)')
    
    # add support lines
    ax.axvline(x=25, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=1225, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Position along bridge (mm)', fontsize=12)
    ax.set_ylabel('Factor of Safety (FOS)', fontsize=12)
    ax.set_title(f'Factor of Safety Along Bridge\nmin FOS: {failure_results["overall_min_fos"]}, failure load: {failure_results["failure_load"]}N', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_failure_loads(failure_results, save_path=None):
    """
    plot Vfail and Mfail along bridge length
    
    Input = 
        failure_results: dict from calculate_failure_loads()
        save_path: path to save figure (optional)
    """
    x = failure_results['x']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # plot Vfail
    ax1.plot(x, failure_results['Vfail_shear'], label='Matboard Shear Failure', linewidth=2)
    ax1.plot(x, failure_results['Vfail_glue'], label='Glue Failure', linewidth=2)
    ax1.plot(x, failure_results['Vfail_buckV'], label='Shear Buckling', linewidth=2)
    ax1.plot(x, failure_results['V_env'], 'k--', label='Applied Shear (V_env)', linewidth=2)
    
    ax1.axvline(x=25, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Supports')
    ax1.axvline(x=1225, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Position along bridge (mm)', fontsize=12)
    ax1.set_ylabel('Shear Force (N)', fontsize=12)
    ax1.set_title('Shear Force Capacities (Vfail)', fontsize=14)
    ax1.legend(loc='best')
    
    # plot Mfail
    ax2.plot(x, failure_results['Mfail_tens'], label='Tension Failure', linewidth=2)
    ax2.plot(x, failure_results['Mfail_comp'], label='Compression Failure', linewidth=2)
    ax2.plot(x, failure_results['Mfail_buck1'], label='Flexural Buckling Case 1', linewidth=1.5, linestyle='--')
    ax2.plot(x, failure_results['Mfail_buck2'], label='Flexural Buckling Case 2', linewidth=1.5, linestyle='--')
    ax2.plot(x, failure_results['Mfail_buck3'], label='Flexural Buckling Case 3', linewidth=1.5, linestyle='--')
    ax2.plot(x, failure_results['M_env'], 'k--', label='Applied Moment (M_env)', linewidth=2)
    
    ax2.axvline(x=25, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Supports')
    ax2.axvline(x=1225, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Position along bridge (mm)', fontsize=12)
    ax2.set_ylabel('Bending Moment (N·mm)', fontsize=12)
    ax2.set_title('Bending Moment Capacities (Mfail)', fontsize=14)
    ax2.legend(loc='best')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_all_for_design(geometry, loadcase, mass, design_name, output_dir):
    """
    generate all required plots for a design
    
    Input = 
        geometry: bridge geometry dict
        loadcase: 1, 2, or 3
        mass: train mass (N)
        design_name: name of design (for filenames)
        output_dir: directory to save plots
    
    creates:
        - SFE and BME plots
        - FOS along bridge
        - Vfail and Mfail plots
    """
    # create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # get material properties
    matboard = get_matboard_properties()
    glue = get_glue_properties()
    material_props = {**matboard, **glue}
    
    # calculate failure loads
    failure_results = calculate_failure_loads(geometry, loadcase, mass, material_props)
    
    # generate plots
    plot_sfe_bme(loadcase, mass, save_path=os.path.join(output_dir, f'{design_name}_sfe_bme.png'))
    plot_fos_along_bridge(failure_results, save_path=os.path.join(output_dir, f'{design_name}_fos.png'))
    plot_failure_loads(failure_results, save_path=os.path.join(output_dir, f'{design_name}_failure_loads.png'))

    return failure_results
